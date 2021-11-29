from kvdroid.jclass.android.net import Uri

from kvdroid.jclass.android.content import Intent
from kvdroid import activity


def make_call(tel):
    intent = Intent(Intent.ACTION_CALL, Uri.parse(f"tel:{tel}"))
    activity.startActivity(intent)


def dial_call(tel):
    intent = Intent(Intent.ACTION_DIAL, Uri.parse(f"tel:{tel}"))
    activity.startActivity(intent)
