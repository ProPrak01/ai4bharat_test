"""
Custom exception handlers and error responses.
"""
from rest_framework.views import exception_handler
from rest_framework.response import Response
from rest_framework import status
import logging

logger = logging.getLogger(__name__)


def custom_exception_handler(exc, context):
    """
    Custom exception handler for consistent error responses.
    """
    # Call REST framework's default exception handler first,
    # to get the standard error response.
    response = exception_handler(exc, context)

    if response is not None:
        custom_response_data = {
            'error': True,
            'message': 'An error occurred',
            'details': {},
            'status_code': response.status_code
        }

        # Handle validation errors
        if response.status_code == status.HTTP_400_BAD_REQUEST:
            custom_response_data['message'] = 'Validation failed'
            custom_response_data['details'] = response.data

        # Handle authentication errors
        elif response.status_code == status.HTTP_401_UNAUTHORIZED:
            custom_response_data['message'] = 'Authentication required'
            custom_response_data['details'] = response.data

        # Handle permission errors
        elif response.status_code == status.HTTP_403_FORBIDDEN:
            custom_response_data['message'] = 'Permission denied'
            custom_response_data['details'] = response.data

        # Handle not found errors
        elif response.status_code == status.HTTP_404_NOT_FOUND:
            custom_response_data['message'] = 'Resource not found'
            custom_response_data['details'] = response.data

        # Handle method not allowed
        elif response.status_code == status.HTTP_405_METHOD_NOT_ALLOWED:
            custom_response_data['message'] = 'Method not allowed'
            custom_response_data['details'] = response.data

        # Handle server errors
        elif response.status_code >= 500:
            custom_response_data['message'] = 'Internal server error'
            custom_response_data['details'] = {'error': 'Something went wrong on our end'}
            logger.error(f'Server error: {exc}', exc_info=True)

        else:
            custom_response_data['message'] = str(exc)
            custom_response_data['details'] = response.data

        response.data = custom_response_data

    return response


def success_response(data=None, message="Success", status_code=status.HTTP_200_OK):
    """
    Helper function for consistent success responses.
    """
    response_data = {
        'success': True,
        'message': message,
        'data': data
    }
    return Response(response_data, status=status_code)


def error_response(message="An error occurred", details=None, status_code=status.HTTP_400_BAD_REQUEST):
    """
    Helper function for consistent error responses.
    """
    response_data = {
        'error': True,
        'message': message,
        'details': details or {},
        'status_code': status_code
    }
    return Response(response_data, status=status_code)