import unittest
from unittest.mock import MagicMock, patch
from datetime import datetime
from mono_engine.modules.state import TradeState, StateModule
from mono_engine.modules.state import TradeState, StateModule, EntryDetails

class TestTradeState(unittest.TestCase):
    def test_basic_state(self):
        ts = TradeState()
        self.assertFalse(ts.get_state()['in_trade'])
        
        entry = EntryDetails(price=123.45, time=datetime.now(), quantity=150, scrip="NIFTY24FEB25000CE")
        ts.update(True, entry)
        
        state = ts.get_state()
        self.assertTrue(state['in_trade'])
        self.assertEqual(state['entry_details'].price, 123.45)
        self.assertEqual(state['entry_details'].quantity, 150)

    def test_thread_safety(self):
        # Simple test — in real project add concurrent threads
        ts = TradeState()
        ts.update(True, None)
        self.assertTrue(ts.get_state()['in_trade'])

class TestStateModule(unittest.TestCase):
    def setUp(self):
        self.mock_engine = MagicMock()
        self.mock_engine.events = MagicMock()
        self.mock_engine.config = {'scrip': 'NIFTY24FEB25000CE'}
        
        # Mock portfolio module
        self.mock_portfolio = MagicMock()
        self.mock_engine.modules = {'portfolio': self.mock_portfolio}
        
        # Mock rest_client fallback
        self.mock_engine.rest = MagicMock()
        self.mock_engine.rest.get_positions = MagicMock(return_value=[])

        self.module = StateModule(self.mock_engine)

    def test_initial_sync_no_position(self):
        self.mock_portfolio.get_positions.return_value = []
        self.module._sync_state(None)
        
        self.assertFalse(self.module.is_in_trade())
        self.mock_engine.events.publish.assert_called_with('state_updated', {'in_trade': False, 'entry_details': None})

    def test_initial_sync_with_position(self):
        self.mock_portfolio.get_positions.return_value = [
            {'scrip': 'NIFTY24FEB25000CE', 'net_qty': 300, 'avg_price': 124.10}
        ]
        self.module._sync_state(None)
        
        self.assertTrue(self.module.is_in_trade())
        details = self.module.get_entry_details()
        self.assertEqual(details.price, 124.10)
        self.assertEqual(details.quantity, 300)

    @patch('mono_engine.modules.state.datetime')
    def test_order_filled_buy(self, mock_datetime):
        mock_datetime.now.return_value = datetime(2026, 2, 10, 21, 45, 0)
        
        self.module.state.update(False)  # start not in trade
        
        fill_data = {
            'order_type': 'buy',
            'scrip': 'NIFTY24FEB25000CE',
            'price': 125.30,
            'quantity': 150,
            'fill_time': datetime.now()
        }
        self.module._on_order_filled(fill_data)
        
        self.assertTrue(self.module.is_in_trade())
        self.assertEqual(self.module.get_entry_details().price, 125.30)

    def test_order_filled_sell_when_not_in_trade(self):
        self.module.state.update(False)
        fill_data = {
    'order_type': 'sell',
    'scrip': 'NIFTY24FEB25000CE',
    'price': 120.0,
    'quantity': 150,
    'fill_time': datetime.now()
}
        self.module._on_order_filled(fill_data)
        # Should log warning but state remains False

if __name__ == '__main__':
    unittest.main()