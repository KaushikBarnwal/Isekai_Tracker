import brevo_python
from brevo_python.rest import ApiException
from django.conf import settings

def send_loot_email(user_email, player_name, item_name, rarity, template_id):
    configuration = brevo_python.Configuration()
    configuration.api_key['api-key'] = settings.BREVO_API_KEY
    api_instance = brevo_python.TransactionalEmailsApi(brevo_python.ApiClient(configuration))
    send_smtp_email = brevo_python.SendSmtpEmail(
        to=[{"email": user_email, "name": player_name}],
        template_id=template_id,
        params={
            "player_name": player_name,
            "item_name": item_name,
            "rarity": rarity
        }
    )
    try:
        api_instance.send_transac_email(send_smtp_email)
        print(f"Loot mail sent to {player_name}!")
    except ApiException as e:
        print(f"Exception when calling Brevo API: {e}")