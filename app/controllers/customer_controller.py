from flask import abort, Blueprint, request, make_response
from app.services.customer_service import get_customers, get_customer_by_id, create_customer, update_customer, \
    patch_customer, delete_customer
from app.logger_config import setup_logger
from app.performance_monitor import log_duration
from app.redis_cache import redis_cache
from flask_restx import Api, Resource, fields, Namespace
from functools import wraps
import jwt
import os
from dotenv import load_dotenv

load_dotenv()

# Logger setup
logger = setup_logger("customer_controller")

# Create Blueprint and Api instance
customers_bp = Blueprint('customers', __name__)
customers_api = Api(customers_bp, title='Customer API', description='API for customer management')

# Create Namespace for customer-related operations
customers_ns = Namespace('customers', description="Operations related to customer management")
customers_api.add_namespace(customers_ns)

# Load secret key from environment variables
SECRET_KEY = os.getenv("SECRET_KEY")

# Swagger model for a customer
customer_model = customers_ns.model('Customer', {
    'name': fields.String(required=False, description='Name of the customer'),
    'address': fields.String(required=False, description='Address of the customer')
})


# Decorator for token validation
def token_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        token = request.headers.get("Authorization")
        if not token:
            abort(403, "Token is missing!")

        try:
            # Devide key for "Bearer" and key itself
            token = token.split()[1] if "Bearer" in token else token
            jwt.decode(token, SECRET_KEY, algorithms=["HS256"])
        except jwt.ExpiredSignatureError:
            abort(401, "Token has expired")
        except jwt.InvalidTokenError:
            abort(403, "Invalid token")

        return f(*args, **kwargs)

    return decorated


# Route to get all customers
# Correct the import statements and definitions as they are already done properly
# Route to get all customers
@customers_ns.route('/')
class CustomerList(Resource):
    @customers_ns.doc('get_customers')
    @customers_ns.response(200, 'Success')
    @customers_ns.response(403, 'Token is missing!')
    @log_duration
    @token_required
    @redis_cache(redis_key="customers:all", ttl=3600)
    def get(self):
        """GET all customers"""
        customers = get_customers()
        return make_response(customers, 200)

    @customers_ns.doc('create_customer')
    @customers_ns.expect(customer_model, validate=True)
    @customers_ns.response(201, 'Customer created successfully')
    @log_duration
    @token_required
    def post(self):
        """POST create new customer"""
        data = request.json
        response, status = create_customer(data)
        return response, status  # Return data directly


# Route for operations on a specific customer by ID
@customers_ns.route('/<int:customer_id>')
@customers_ns.param('customer_id', 'The ID of the customer')
class Customer(Resource):
    @customers_ns.doc('get_customer')
    @customers_ns.response(200, 'Success')
    @customers_ns.response(404, 'Customer not found')
    @log_duration
    @token_required
    @redis_cache(redis_key="customer:by_id", ttl=3600)
    def get(self, customer_id):
        """GET customer by ID"""
        customer = get_customer_by_id(customer_id)
        if customer:
            logger.info(f"Customer with id={customer_id} found, customer data: {customer}")
            return customer, 200  # Return data directly
        else:
            logger.error(f"Customer with id={customer_id} not found in database")
            return {'error': 'Customer not found'}, 404  # Return as a dictionary

    @customers_ns.doc('update_customer')
    @customers_ns.expect(customer_model, validate=True)
    @customers_ns.response(200, 'Customer updated successfully')
    @log_duration
    @token_required
    def put(self, customer_id):
        """PUT update customer"""
        data = request.json
        response, status = update_customer(customer_id, data)
        return response, status  # Return data directly

    @customers_ns.doc('patch_customer', validate=False)
    @customers_ns.expect(customer_model)
    @customers_ns.response(200, 'Customer patched successfully')
    @log_duration
    @token_required
    def patch(self, customer_id):
        """PATCH update customer"""
        data = request.json
        response, status = patch_customer(customer_id, data)
        return response, status  # Return data directly

    @customers_ns.doc('delete_customer')
    @customers_ns.response(200, 'Customer deleted successfully')
    @customers_ns.response(404, 'Customer not found')
    @log_duration
    @token_required
    def delete(self, customer_id):
        """DELETE customer by ID"""
        response, status = delete_customer(customer_id)
        return response, status  # Return data directly
