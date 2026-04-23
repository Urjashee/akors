from ninja import Router
from django.db import transaction
from django.db.models import Count

from accounts.models import Role, Title, Subscriptions
from accounts.schemas import SuccessSchema, ErrorSchema
from property.models import State, UnitClass, UnitType

router = Router(tags=["config"])

@router.get(
    "/get",
    auth=None,
    response={ 200: SuccessSchema, 400: ErrorSchema },
)
def get_config_details(request):
    try:
        with transaction.atomic():
            roles = Role.objects.values("id", "name")
            titles = Title.objects.values("id", "name")
            states = State.objects.annotate(forms_count=Count("forms")).values("id", "name", "is_active", "forms_count")
            unit_classes = UnitClass.objects.values("id", "name")
            unit_types = UnitType.objects.values("id", "name")
            subscriptions = Subscriptions.objects.values("id", "name", "amount", "external_id", "units")

            data = {
                "roles": list(roles),
                "titles": list(titles),
                "subscriptions": list(subscriptions),
                "states": list(states),
                "unit_classes": list(unit_classes),
                "unit_types": list(unit_types),
            }

            return 200, {
                "status": "SUCCESS",
                "message": "Successfully created operator account.",
                "data": data
            }


    except Exception as e:
        import traceback
        traceback.print_exc()  # prints full stacktrace in console/logs
        return 400, {
            "status": "ERROR",
            "message": str(e),
        }
