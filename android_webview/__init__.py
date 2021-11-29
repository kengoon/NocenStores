# Android **only** HTML viewer, always full screen.
#
# Back button or gesture has the usual browser behavior, except for the final
# back event which returns the UI to the view before the browser was opened.
#
# Base Class:  https://kivy.org/doc/stable/api-kivy.uix.modalview.html
#
# Requires: android.permissions = INTERNET
# Uses:     orientation = landscape, portrait, or all
# Arguments:
# url               : required string,  https://   file:// (content://  ?)
# enable_javascript : optional boolean, defaults False
# enable_downloads  : optional boolean, defaults False
# enable_zoom       : optional boolean, defaults False
#
# Downloads are delivered to app storage see downloads_directory() below.
#
# Tested on api=27 and api=30
#
# Note:
#    For api>27   http://  gives net::ERR_CLEARTEXT_NOT_PERMITTED
#    This is Android implemented behavior.
#
# Source https://github.com/Android-for-Python/Webview-Example
from kivy.clock import mainthread
from kivy.properties import BooleanProperty, StringProperty
from kivy.uix.modalview import ModalView
from kivy.core.window import Window
from android.runnable import run_on_ui_thread
from jnius import autoclass, cast, PythonJavaClass, java_method
from kivymd.toast import toast

from classes.notification import notify

Environment = autoclass('android.os.Environment')
Context = autoclass('android.content.Context')
PythonActivity = autoclass('org.kivy.android.PythonActivity')


class DownloadListener(PythonJavaClass):
    # https://stackoverflow.com/questions/10069050/download-file-inside-webview
    __javacontext__ = 'app'
    __javainterfaces__ = ['android/webkit/DownloadListener']

    @java_method('(Ljava/lang/String;Ljava/lang/String;Ljava/lang/String;Ljava/lang/String;J)V')
    def onDownloadStart(self, url, userAgent, contentDisposition, mimetype,
                        contentLength):
        DownloadManagerRequest = autoclass('android.app.DownloadManager$Request')
        DownloadManager = autoclass('android.app.DownloadManager')
        Uri = autoclass('android.net.Uri')
        mActivity = PythonActivity.mActivity
        context = mActivity.getApplicationContext()
        visibility = DownloadManagerRequest.VISIBILITY_VISIBLE_NOTIFY_COMPLETED
        dir_type = Environment.DIRECTORY_DOWNLOADS
        uri = Uri.parse(url)
        filepath = uri.getLastPathSegment()
        request = DownloadManagerRequest(uri)
        request.setNotificationVisibility(visibility)
        request.setDestinationInExternalFilesDir(context, dir_type, filepath)
        dm = cast(DownloadManager,
                  mActivity.getSystemService(Context.DOWNLOAD_SERVICE))
        dm.enqueue(request)


class KeyListener(PythonJavaClass):
    __javacontext__ = 'app'
    __javainterfaces__ = ['android/view/View$OnKeyListener']

    def __init__(self, listener):
        super().__init__()
        self.listener = listener

    @java_method('(Landroid/view/View;ILandroid/view/KeyEvent;)Z')
    def onKey(self, v, key_code, event):
        KeyEvent = autoclass('android.view.KeyEvent')
        if event.getAction() == KeyEvent.ACTION_DOWN and \
                key_code == KeyEvent.KEYCODE_BACK:
            return self.listener()


class WebView(ModalView):
    # https://developer.android.com/reference/android/webkit/WebView
    enable_javascript = BooleanProperty(False)
    enable_downloads = BooleanProperty(False)
    enable_zoom = BooleanProperty(False)
    url = StringProperty()

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.initiate_webview()
        self.ViewGroup = None
        self.LayoutParams = None
        self.mActivity = PythonActivity.mActivity
        self.webview = None
        self.layout = None

    @run_on_ui_thread
    def initiate_webview(self):
        WebViewA = autoclass('android.webkit.WebView')
        WebViewClient = autoclass('android.webkit.WebViewClient')
        LinearLayout = autoclass('android.widget.LinearLayout')
        self.ViewGroup = autoclass('android.view.ViewGroup')
        self.LayoutParams = autoclass('android.view.ViewGroup$LayoutParams')
        self.webview = WebViewA(self.mActivity)
        self.webview.setWebViewClient(WebViewClient())
        self.webview.getSettings().setJavaScriptEnabled(self.enable_javascript)
        self.webview.getSettings().setBuiltInZoomControls(self.enable_zoom)
        self.webview.getSettings().setDisplayZoomControls(False)
        self.webview.getSettings().setAllowFileAccess(True)  # default False api>29
        self.layout = LinearLayout(self.mActivity)
        self.layout.setOrientation(LinearLayout.VERTICAL)

    @run_on_ui_thread
    def on_open(self):
        self.layout.addView(self.webview, self.width, self.height)
        self.mActivity.addContentView(self.layout, self.LayoutParams(-1, -1))
        self.webview.setOnKeyListener(KeyListener(self._back_pressed))
        toast("Loading......", length_long=True, gravity=80)
        if self.enable_downloads:
            self.webview.setDownloadListener(DownloadListener())
        try:
            self.webview.loadUrl("about:blank")
            self.webview.loadUrl(self.url)
        except Exception as e:
            print('Webview.on_open(): ' + str(e))
            self.dismiss()

    @run_on_ui_thread
    def on_dismiss(self):
        self.layout.removeView(self.webview)
        parent = cast(self.ViewGroup, self.layout.getParent())
        if parent:
            parent.removeView(self.layout)
        self.webview.clearHistory()
        self.webview.clearCache(True)
        self.webview.clearFormData()
        # self.webview.destroy()

    # @run_on_ui_thread
    # def on_size(self, instance, size):
    #     if self.webview:
    #         params = self.webview.getLayoutParams()
    #         params.width = Window.width
    #         params.height = Window.height
    #         self.webview.setLayoutParams(params)

    def pause(self):
        if self.webview:
            self.webview.pauseTimers()
            self.webview.onPause()

    def resume(self):
        if self.webview:
            self.webview.onResume()
            self.webview.resumeTimers()

    @staticmethod
    def downloads_directory():
        # e.g. Android/data/org.test.myapp/files/Download
        dir_type = Environment.DIRECTORY_DOWNLOADS
        context = PythonActivity.mActivity.getApplicationContext()
        directory = context.getExternalFilesDir(dir_type)
        return str(directory.getPath())

    def _back_pressed(self):
        # if self.webview.canGoBack():
        #     self.webview.goBack()
        # else:
        self.dismiss()
        return True
