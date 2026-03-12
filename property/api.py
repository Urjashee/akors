from ninja import Router
from django.db import transaction

from accounts.auth_roles_middleware import OperatorAuth, SuperAdminAuth
from accounts.schemas import SuccessSchema, ErrorSchema
from property.models import State, PropertyManagement
from property.schemas import AddProperty

router = Router(tags=["property"])

#  *************************** ADMIN **************************************



#  *************************** PROPERT MANAGER **************************************



#  *************************** OPERATOR **************************************

@router.post(
    "/operator/add-edit",
    auth=OperatorAuth(),
    response={ 200: SuccessSchema, 400: ErrorSchema, 403: ErrorSchema },
)
def add_edit_property(request, payload: AddProperty):

    try:
        with transaction.atomic():
            if payload.id:
                property = PropertyManagement.objects.get(id=payload.id)


            else:
                property = PropertyManagement.objects.create(
                    name=payload.name,
                    state_id=payload.state_id,
                )
                if not property:
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