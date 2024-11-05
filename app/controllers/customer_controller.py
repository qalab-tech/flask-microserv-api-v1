from flask import abort, Blueprint, jsonify, request, make_response
from app.services.customer_service import get_customers, get_customer_by_id, create_customer, update_customer, \
    delete_customer
from app.logger_config import setup_logger
from flask_restx import Api, Resource, fields, Namespace
from functools import wraps
import jwt
import os

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
    'name': fields.String(required=True, description='Name of the customer'),
    'address': fields.String(required=True, description='Address of the customer')
})


# Decorator for token validation
def token_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        auth_header = request.headers.get('Authorization')

        if not auth_header:
            return jsonify({'message': 'Token is missing!'}), 401

        token_parts = auth_header.split(" ")
        if len(token_parts) != 2 or token_parts[0] != 'Bearer':
            return jsonify({'message': 'Token is invalid!'}), 401  # If token format is incorrect

        token = token_parts[1]
        try:
            # Decoding a token with expiration check
            jwt.decode(token, SECRET_KEY, algorithms=["HS256"])

        except jwt.ExpiredSignatureError:
            # Token expired
            return jsonify({'message': 'Token is expired!'}), 401
        except jwt.InvalidTokenError:
            # Invalid token
            return jsonify({'message': 'Invalid token!'}), 403

        return f(*args, **kwargs)

    return decorated


# Route to get all customers
# Correct the import statements and definitions as they are already done properly

# Adjusted route paths
# Route to get all customers
@customers_ns.route('/')
class CustomerList(Resource):
    @customers_ns.doc('get_customers')
    @customers_ns.response(200, 'Success')
    @customers_ns.response(403, 'Token is missing!')
    @token_required
    def get(self):
        """GET all customers"""
        customers = get_customers()
        return jsonify(customers, 200)  # Return data directly

    @customers_ns.doc('create_customer')
    @customers_ns.expect(customer_model, validate=True)
    @customers_ns.response(201, 'Customer created successfully')
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
    @token_required
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
    @token_required
    def put(self, customer_id):
        """PUT update customer"""
        data = request.json
        response, status = update_customer(customer_id, data)
        return response, status  # Return data directly

    @customers_ns.doc('delete_customer')
    @customers_ns.response(200, 'Customer deleted successfully')
    @customers_ns.response(404, 'Customer not found')
    @token_required
    def delete(self, customer_id):
        """DELETE customer by ID"""
        response, status = delete_customer(customer_id)
        return response, status  # Return data directly
