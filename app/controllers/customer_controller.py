from flask import Blueprint, jsonify, request
from app.services.customer_service import get_customers, get_customer_by_id, create_customer, update_customer, \
    delete_customer
from app.logger_config import setup_logger

logger = setup_logger("customer_controller")
customer_bp = Blueprint('customers', __name__)


@customer_bp.route('/', methods=['GET'])
def get_customers_route():
    """GET all customers"""
    customers = get_customers()
    return jsonify(customers), 200


@customer_bp.route('/', methods=['POST'])
def create_customer_route():
    """POST create new customer"""
    data = request.json
    response, status = create_customer(data)
    return jsonify(response), status


@customer_bp.route('/<int:customer_id>', methods=['GET'])
def get_customer_route(customer_id):
    """GET customer by id"""
    customer = get_customer_by_id(customer_id)
    if customer:
        logger.info(f"Customer with id={customer_id} found, customer data: {str(customer)}")
        return jsonify(customer), 200
    else:
        logger.error(f"Customer with id={customer_id} not found in database")
        return jsonify({"error": "Customer not found"}), 404


@customer_bp.route('/<int:customer_id>', methods=['PUT'])
def update_customer_route(customer_id):
    """PUT update customer"""
    data = request.json
    response, status = update_customer(customer_id, data)
    return jsonify(response), status


@customer_bp.route('/<int:customer_id>', methods=['DELETE'])
def delete_customer_route(customer_id):
    """DELETE customer by ID"""
    response, status = delete_customer(customer_id)
    return jsonify(response), status
