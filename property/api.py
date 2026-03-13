from ninja import Router
from django.db import transaction

from accounts.auth_roles_middleware import OperatorAuth, SuperAdminAuth
from accounts.models import User
from accounts.schemas import SuccessSchema, ErrorSchema
from property.models import State, PropertyManagement
from property.schemas import AddProperty, AssignManager, PropertySchema
from accounts.constants import PROPERTY_MANAGER, SUPER_ADMIN, OPERATOR
from property.services import update_property_forms

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
        "data": None
    }


#  *************************** PROPERT MANAGER **************************************

from forms.models import Forms
from property.models import PropertyForms

@router.get(
    "/get",
    response={200: SuccessSchema[list[PropertySchema]], 400: ErrorSchema},
)
def get_property(request):

    buildings = (
        PropertyManagement.objects
        .select_related("state")
        .filter(manager=request.user)
    )

    result = []

    for building in buildings:

        state_forms = Forms.objects.filter(state=building.state).select_related("state")

        active_forms = set(
            PropertyForms.objects
            .filter(property=building)
            .values_list("form_id", flat=True)
        )
        print(active_forms)

        forms = []

        for form in state_forms:
            forms.append({
                "id": form.id,
                "name": form.name,
                "image": form.image.url if form.image else None,
                "active": 1 if form.id in active_forms else 0
            })

        result.append({
            "id": building.id,
            "name": building.name,
            "address_line_1": building.address_line_1,
            "address_line_2": building.address_line_2,
            "city": building.city,
            "zipcode": building.zipcode,
            "property_management_company": building.property_management_company,
            "state_registration": building.state_registration,
            "state": {
                "id": building.state.id,
                "name": building.state.name
            },
            "forms": forms
        })

    return 200, {
        "status": "SUCCESS",
        "message": "Successfully fetched buildings.",
        "data": result
    }


#  *************************** OPERATOR **************************************

@router.post(
    "/add-edit",
    response={200: SuccessSchema, 400: ErrorSchema, 403: ErrorSchema},
)
def add_edit_property(request, payload: AddProperty):
    try:
        state = State.objects.get(id=payload.state_id)
        with transaction.atomic():
            if payload.id:
                property_management = PropertyManagement.objects.get(id=payload.id)
                property_management.name = payload.name
                property_management.property_management_company = payload.property_management_company
                property_management.address_line_1 = payload.address_line_1
                property_management.address_line_2 = payload.address_line_2
                property_management.city = payload.city
                property_management.zipcode = payload.zipcode
                property_management.state = state
                if request.user.role.id is OPERATOR:
                    property_management.state_registration = payload.state_registration
                if request.user.role.id is SUPER_ADMIN:
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
                    property_management.state_registration = payload.state_registration
                    property_management.manager_id = payload.manager_id
                property_management.save()
                if request.user.role.id is PROPERTY_MANAGER:
                    update_property_forms(property_management, payload)

            else:
                print(request.user.role)
                if request.user.role.id is not OPERATOR:
                    return 400, {
                        "status": "ERROR",
                        "message": "Can't add building details",
                    }

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
        "data": None
    }
