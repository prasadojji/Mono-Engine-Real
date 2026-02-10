import unittest
from unittest.mock import MagicMock, patch
from datetime import datetime
from typing import Dict
from mono_engine.modules.order import Order, ORDER_TYPES  # Import your Order class and constants
from unittest.mock import ANY

class TestOrderModule(unittest.TestCase):
    def setUp(self):
        self.mock_engine = MagicMock()
        self.mock_engine.events = MagicMock()
        self.mock_engine.config = {
            'scrip': 'NIFTY24FEB25000CE',
            'lot_size': 50,
            'retry_attempts': 1,  # Set to 1 for faster tests
            'retry_delay': 0
        }
        # Mock session and rest
        self.mock_session = MagicMock()
        self.mock_session.is_logged_in.return_value = True
        self.mock_session.rest.post.return_value = {'s': 'ok', 'd': {'order_id': 'TEST123'}}
        self.mock_engine.session = self.mock_session
        # Mock state module
        self.mock_state = MagicMock()
        self.mock_engine.modules = {'state': self.mock_state}
        
        self.module = Order(self.mock_engine)

    def test_init(self):
        self.assertEqual(self.module.scrip, 'NIFTY24FEB25000CE')
        self.assertEqual(self.module.lot_size, 50)
        self.assertDictEqual(self.module.pending_orders, {})

    def test_start_stop(self):
        self.module.start()
        self.mock_engine.events.subscribe.assert_any_call('buy_signal', self.module._handle_buy_signal)
        self.mock_engine.events.subscribe.assert_any_call('sell_signal', self.module._handle_sell_signal)
        self.mock_engine.events.subscribe.assert_any_call('on_order_update', self.module._on_order_update)
        
        self.module.stop()
        self.assertNotIn('buy_signal', self.mock_engine.events.callbacks)

    @patch('mono_engine.modules.order.sleep')  # Mock sleep for retries
    def test_place_order_success(self, mock_sleep):
        resp = self.module.place_order(
            symbol='NIFTY24FEB25000CE',
            quantity=100,
            side='buy',
            order_type='market'
        )
        self.assertEqual(resp['s'], 'ok')
        self.mock_session.rest.post.assert_called_once()
        self.mock_engine.events.publish.assert_not_called()  # Not called here; handled in signals

    @patch('mono_engine.modules.order.sleep')
    def test_place_order_retry_fail(self, mock_sleep):
        self.mock_session.rest.post.side_effect = Exception("API error")
        resp = self.module.place_order(
            symbol='NIFTY24FEB25000CE',
            quantity=100,
            side='buy',
            order_type='market'
        )
        self.assertIsNone(resp)
        self.mock_session.rest.post.assert_called_once()  # Since retry_attempts=1

    def test_handle_buy_signal(self):
        self.mock_state.is_in_trade.return_value = False
        signal_data = {'quantity': 2, 'order_type': 'LIMIT', 'price': 125.0}
        self.module._handle_buy_signal(signal_data)
        
        self.mock_engine.events.publish.assert_any_call('pre_order', {'action': 'buy', **signal_data, 'scrip': self.module.scrip})
        self.mock_session.rest.post.assert_called_once()  # place_order called
        self.assertIn('TEST123', self.module.pending_orders)
        self.mock_engine.events.publish.assert_any_call('order_placed', {'order_id': 'TEST123', 'side': 'buy', 'scrip': self.module.scrip})

    def test_handle_buy_signal_in_trade(self):
        self.mock_state.is_in_trade.return_value = True
        self.module._handle_buy_signal({'quantity': 1})
        self.mock_session.rest.post.assert_not_called()  # Ignored due to state

    def test_handle_sell_signal(self):
        self.mock_state.is_in_trade.return_value = True
        signal_data = {'quantity': 2, 'order_type': 'MARKET'}
        self.module._handle_sell_signal(signal_data)
        
        self.mock_session.rest.post.assert_called_once()
        self.assertIn('TEST123', self.module.pending_orders)

    def test_on_order_update_filled(self):
        self.module.pending_orders['TEST123'] = {'side': 'buy', 'quantity': 100, 'filled': 0}
        update_data = {'order_id': 'TEST123', 'status': 'FILLED', 'filled_qty': 100, 'price': 124.5}
        self.module._on_order_update(update_data)
        
        self.assertNotIn('TEST123', self.module.pending_orders)
        self.mock_engine.events.publish.assert_called_with('order_filled', {
            'order_type': 'buy', 'scrip': self.module.scrip, 'price': 124.5, 
            'quantity': 100 // 50, 'fill_time': update_data.get('fill_time', ANY)
        })

    def test_on_order_update_partial(self):
        self.module.pending_orders['TEST123'] = {'side': 'sell', 'quantity': 100, 'filled': 0}
        self.module._on_order_update({'order_id': 'TEST123', 'status': 'PARTIAL', 'filled_qty': 50})
        self.assertEqual(self.module.pending_orders['TEST123']['filled'], 50)
        self.mock_engine.events.publish.assert_not_called()  # Not full yet

    def test_on_order_update_rejected(self):
        self.module.pending_orders['TEST123'] = {'side': 'buy', 'quantity': 100, 'filled': 0}
        update_data = {'order_id': 'TEST123', 'status': 'REJECTED', 'reason': 'Insufficient margin'}
        self.module._on_order_update(update_data)
        
        self.assertNotIn('TEST123', self.module.pending_orders)
        self.mock_engine.events.publish.assert_called_with('order_rejected', {**update_data, 'scrip': self.module.scrip})

    def test_modify_order(self):
        self.module.pending_orders['TEST123'] = {'quantity': 100}
        self.mock_session.rest.post.return_value = {'s': 'ok'}
        resp = self.module.modify_order('TEST123', new_price=126.0, new_quantity=3)
        
        self.assertEqual(resp['s'], 'ok')
        self.assertEqual(self.module.pending_orders['TEST123']['quantity'], 3 * 50)  # Updated

    def test_exit_order(self):
        self.module.pending_orders['TEST123'] = {}
        self.mock_session.rest.post.return_value = {'s': 'ok'}
        resp = self.module.exit_order('TEST123')
        
        self.assertEqual(resp['s'], 'ok')
        self.assertNotIn('TEST123', self.module.pending_orders)
        self.mock_engine.events.publish.assert_called_with('order_canceled', {'order_id': 'TEST123', 'scrip': self.module.scrip})

if __name__ == '__main__':
    unittest.main()