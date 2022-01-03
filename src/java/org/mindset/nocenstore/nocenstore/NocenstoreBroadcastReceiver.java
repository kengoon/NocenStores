package org.mindset.nocenstore.nocenstore;

import android.content.BroadcastReceiver;
import android.content.Intent;
import android.content.Context;

public class NocenstoreBroadcastReceiver extends BroadcastReceiver {
    public void onReceive(Context context, Intent intent) {
        System.out.println("---------------on-boot-started-------------------");
        ServiceNotification.start(context, "");
        System.out.println("---------------on-boot-completed----------------");
    }
}
