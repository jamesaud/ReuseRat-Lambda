print("Loading Function...")
import shopify
import os
from datetime import date



SHOPIFY_API_KEY = os.getenv("SHOPIFY_API_KEY")
SHOPIFY_PASSWORD = os.getenv("SHOPIFY_PASSWORD")
SHOPIFY_APP_NAME = os.getenv("SHOPIFY_APP_NAME")

DAYS_TO_DECREASE_PRICE = os.getenv("DAYS_TO_DECREASE_PRICE")  # Days to wait before decreasing price
PERCENT_TO_DECREASE = os.getenv("PERCENT_TO_DECREASE")


### SHOPIFY SETTINGS ###
SHOPIFY_SHOP_URL = "https://{api_key}:{password}@{shop_name}/admin/".format(api_key=SHOPIFY_API_KEY,
                                                                   password=SHOPIFY_PASSWORD,
                                                                   shop_name=SHOPIFY_APP_NAME)

MIN_PRICE_TO_DECREASE = os.getenv("MIN_PRICE_TO_DECREASE")  # In dollars

# Fix import errors by requiring the variable to be set
if PERCENT_TO_DECREASE and PERCENT_TO_DECREASE > 5:
    raise ValueError("Are you sure you want to decrease the price by over 5%?")

if DAYS_TO_DECREASE_PRICE and DAYS_TO_DECREASE_PRICE < 7:
    raise ValueError("Are you sure you want to decrease prices faster than a week?")


def get_product_last_updated_date(product: shopify.product):
    split = product.updated_at.replace("T", "-").split("-")
    year, month, day = int(split[0]), int(split[1]), int(split[2])
    return date(year, month, day)


def should_decrease_price(product: shopify.product):

    # Don't decrease price if it's at 4 dollars or less
    for variant in  product.variants:
        if variant.price < 4:
            return False

    last_updated = get_product_last_updated_date(product)
    today = date.today()
    delta = today - last_updated

    if delta.days >= DAYS_TO_DECREASE_PRICE:
        return True
    else:
        return False


def calculate_amount_to_decrease():
    return 1 - .01 * PERCENT_TO_DECREASE

def decrease_variant_prices(product: shopify.product):
    """Decreases prices of all shopify variants of a product"""
    for variant in product.variants:
        variant.price = float(variant.price) * calculate_amount_to_decrease()


def update_products():
    shopify.ShopifyResource.set_site(SHOPIFY_SHOP_URL)
    shop = shopify.Shop.current()

    products = shopify.Product.find()  # Get a list of all products
    for product in products:
        if should_decrease_price(product):
            print("Decreasing price: {}".format(product))
            decrease_variant_prices(product)
        try:
            product.save()
        except Exception as e:
            print("Failed to Save Product: {}".format(e))

def lambda_handler(event, context):
    update_products()





