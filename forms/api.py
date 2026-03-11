from ninja import Router
from django.db import transaction
from ninja import File
from django.core.files.uploadedfile import UploadedFile

from accounts.auth_roles_middleware import OperatorAuth, SuperAdminAuth
from accounts.schemas import SuccessSchema, ErrorSchema
from property.models import State
from forms.schemas import AddProperty, UpdateStates, AddEditForms

router = Router(tags=["forms"])

#  *************************** ADMIN **************************************
@router.post(
    "/update-states",
    auth=SuperAdminAuth(),
    response={ 200: SuccessSchema, 400: ErrorSchema, 403: ErrorSchema },
)
def update_states(request, payload: UpdateStates):
    try:
        with transaction.atomic():
            for state in payload.states:
                row = State.objects.get(pk=state)
                row.is_active = True
                row.save()

    except Exception as e:
        return 400, {
            "status": "ERROR",
            "message": str(e),
        }

    return 200, {
        "status": "SUCCESS",
        "message": "Successfully updated states.",
    }

# @router.post(
#     "/add-update",
#     auth=SuperAdminAuth(),
#     response={ 200: SuccessSchema, 400: ErrorSchema, 403: ErrorSchema },
# )
# def add_update_form(request, payload: AddEditForms, image: UploadedFile = File(...)):
#     try:
#         with transaction.atomic():
#             pass
#
#     except Exception as e:
#         return 400, {
#             "status": "ERROR",
#             "message": str(e),
#         }
#
#     return 200, {
#         "status": "SUCCESS",
#         "message": "Successfully updated states.",
#     }


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