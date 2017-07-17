SHOPIFY_TEST_API_KEY = "169db5a6b7a2c510655bdc3f4365e404"
SHOPIFY_TEST_PASSWORD = "3622c9b81774e8a9fa413a65651555fe"

from datetime import datetime
from unittest.mock import MagicMock, patch
import shopify
import unittest
from lambda_function import *
import lambda_function

lambda_function.DAYS_TO_DECREASE_PRICE = 7
lambda_function.PERCENT_TO_DECREASE = 5   # Decrease by 5% per week


variant_format =  lambda: {
    "barcode": "1234_pink",
    "compare_at_price": None,
    "created_at": "2012-08-24T14:01:47-04:00",
    "fulfillment_service": "manual",
    "grams": 567,
    "weight": 0.2,
    "weight_unit": "kg",
    "id": 808950810,
    "inventory_management": "shopify",
    "inventory_policy": "continue",
    "inventory_quantity": 10,
    "option1": "Pink",
    "position": 1,
    "price": 199.99,
    "product_id": 632910392,
    "requires_shipping": True,
    "sku": "IPOD2008PINK",
    "taxable": True,
    "title": "Pink",
    "updated_at": "2012-08-24T14:01:47-04:00"
  }



class Tests(unittest.TestCase):

    @patch('shopify.Product')
    def _create_product(self, MockProduct):
        product = MockProduct()
        product.updated_at = str(datetime.utcnow()).replace(" ", "T")  # Mimic how shopify's response looks like
        variant = shopify.Variant(variant_format())
        product.variants = [variant]
        product.variants[0].price = 100.00

        return product

    def setUp(self):
        self.product = self._create_product()

    def test_get_product_last_updated_date(self):
        date_obj = get_product_last_updated_date(self.product)

        # Should be a "date" object, but can't check using 'isinstance(date_obj, date)' for some reason
        self.assertIsInstance(date_obj.day, int)
        self.assertIsInstance(date_obj.month, int)
        self.assertIsInstance(date_obj.year, int)

    def test_should_decrease_price(self):

        # Less than 1 week old, shouldn't decrease price
        bool = should_decrease_price(self.product)
        self.assertFalse(bool)

        # More than 1 week old, should decrease price
        self.product.updated_at = "2012-08-24T14:01:47-04:00"
        bool = should_decrease_price(self.product)
        self.assertTrue(bool)

    def test_calculate_amount_to_decrease(self):
        amount = calculate_amount_to_decrease()
        self.assertTrue(amount, 1 - .01 * lambda_function.PERCENT_TO_DECREASE)

    def test_decrease_variant_prices(self):
        old_price = self.product.variants[0].price
        decrease_variant_prices(self.product)
        new_price = self.product.variants[0].price

        self.assertEqual(old_price * calculate_amount_to_decrease(), new_price)



if __name__ == '__main__':
    unittest.main()