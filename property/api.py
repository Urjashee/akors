from ninja import Router
from django.db import transaction

from accounts.auth_roles_middleware import OperatorAuth, SuperAdminAuth
from accounts.models import User
from accounts.schemas import SuccessSchema, ErrorSchema
from property.models import State, PropertyManagement
from property.schemas import AddProperty, AssignManager
from accounts.constants import PROPERTY_MANAGER

router = Router(tags=["property"])


#  *************************** ADMIN **************************************
@router.post(
    "/admin/assign-manager",
    auth=SuperAdminAuth(),
    response={200: SuccessSchema, 400: ErrorSchema, 403: ErrorSchema},
)
def assign_manager(request, payload: AssignManager):
    user = User.objects.get(id=payload.manager_id)
    if not user:
        return 400, {
            "status": "ERROR",
            "message": "User not found",
        }
    if user.role.id is not PROPERTY_MANAGER:
        return 400, {
            "status": "ERROR",
            "message": "Assigned user is not a property manager",
        }
    try:
        with transaction.atomic():
            property_management = PropertyManagement.objects.get(id=payload.property_id)
            if not property_management:
                return 400, {
                    "status": "ERROR",
                    "message": "Property does not exist",
                }

            property_management.manager = user
            property_management.save()

    except Exception as e:
        return 400, {
            "status": "ERROR",
            "message": str(e),
        }

    return 200, {
        "status": "SUCCESS",
        "message": "Successfully update property manager.",
    }

#  *************************** PROPERT MANAGER **************************************


#  *************************** OPERATOR **************************************

@router.post(
    "/operator/add-edit",
    auth=OperatorAuth(),
    response={200: SuccessSchema, 400: ErrorSchema, 403: ErrorSchema},
)
def add_edit_property(request, payload: AddProperty):
    try:
        state = State.objects.get(id=payload.state_id)
        with transaction.atomic():
            if payload.id:
                property_management = PropertyManagement.objects.get(id=payload.id)
                property_management.name = payload.name
                property_management.state_registration = payload.state_registration
                property_management.property_management_company = payload.property_management_company
                property_management.address_line_1 = payload.address_line_1
                property_management.address_line_2 = payload.address_line_2
                property_management.city = payload.city
                property_management.zipcode = payload.zipcode
                property_management.state = state
                property_management.save()

            else:
                property_management = PropertyManagement.objects.create(
                    name=payload.name,
                    state_registration=payload.state_registration,
                    property_management_company=payload.property_management_company,
                    address_line_1=payload.address_line_1,
                    address_line_2=payload.address_line_2,
                    city=payload.city,
                    zipcode=payload.zipcode,
                    state=state,
                    created_by=request.user,
                )
                if not property_management:
                    return 400, {
                        "status": "ERROR",
                        "message": "Form could not be created.",
                    }

    except Exception as e:
        return 400, {
            "status": "ERROR",
            "message": str(e),
        }

    return 200, {
        "status": "SUCCESS",
        "message": "Successfully added/updated building.",
    }
