from ninja import Router
from django.db import transaction

from accounts.auth_roles_middleware import OperatorAuth, SuperAdminAuth
from accounts.schemas import SuccessSchema, ErrorSchema
from property.models import State
from property.schemas import AddProperty

router = Router(tags=["property"])

#  *************************** ADMIN **************************************



#  *************************** PROPERT MANAGER **************************************



#  *************************** OPERATOR **************************************

@router.post(
    "/property-manager/invite-users",
    auth=OperatorAuth(),
    response={ 200: SuccessSchema, 400: ErrorSchema, 403: ErrorSchema },
)
def property_manager_invite_user(request, payload: AddProperty):

    try:
        with transaction.atomic():
            pass

    except Exception as e:
        return 400, {
            "status": "ERROR",
            "message": str(e),
        }

    return 200, {
        "status": "SUCCESS",
        "message": "Successfully invited operator account.",
    }