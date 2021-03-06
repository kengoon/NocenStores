from kivy.core.window import Window
from kivy.clock import Clock
from jnius import autoclass
from android.runnable import run_on_ui_thread

WebView = autoclass('android.webkit.WebView')
WebViewClient = autoclass('android.webkit.WebViewClient')
ViewGroup = autoclass('android.view.ViewGroup')
LayoutParams = autoclass('android.view.ViewGroup$LayoutParams')
activity = autoclass('org.kivy.android.PythonActivity').mActivity
mWebview = autoclass('org.kivy.android.PythonActivity').mWebview
web_name = "android"


class AndroidWebView(object):

    def open(self, url, new=0, autoraise=True):
        return self.start_webview(url)

    def open_new(self, url):
        return self.start_webview(url)

    def open_new_tab(self, url):
        return self.start_webview(url)

    def start_webview(self, url):
        Window.bind(on_key_down=self.listen_for_key)
        Clock.schedule_once(lambda *args: self.create_webview(url), 0)
        return True

    @run_on_ui_thread
    def create_webview(self, url):
        """ attaching webview to app """
        # self.webview = WebView(activity)
        settings = mWebview.getSettings()

        settings.setJavaScriptEnabled(True)  # enables js
        settings.setDomStorageEnabled(True)
        settings.setUseWideViewPort(True)  # enables viewport html meta tags
        settings.setLoadWithOverviewMode(True)  # uses viewport
        settings.setSupportZoom(True)  # enables zoom

        self.wvc = WebViewClient()
        mWebview.setWebViewClient(self.wvc)
        mWebview.setLayoutParams(LayoutParams(
            LayoutParams.FILL_PARENT,
            LayoutParams.FILL_PARENT))

        activity.getLayout().addView(mWebview)
        mWebview.loadUrl(url)
        activity.rootUrl = url

    def listen_for_key(self, keyboard, keycode, text, *modifiers):
        if keycode == 27:
            self.on_back_button()
        return True

    @run_on_ui_thread
    def on_back_button(self, *args):
        if mWebview:
            if mWebview.canGoBack():
                mWebview.goBack()  # webview going back inline
            else:
                self.detach_webview()

    def detach_webview(self, *args):
        # detaching webview from view port
        Window.unbind(on_key_down=self.listen_for_key)
        if mWebview:
            mWebview.clearHistory()
            mWebview.clearCache(True)
            mWebview.loadUrl("about:blank")
            mWebview.freeMemory()  # probably not needed anymore

            if mWebview.getParent():
                print(mWebview.getParent())
                activity.getLayout().removeView(mWebview)

            # self.webview = None
            self.wvc = None


import webbrowser

webbrowser.register(web_name, AndroidWebView)

if __name__ == '__main__':
    from kivy.app import App
    from kivy.uix.button import Button


    class TestApp(App):

        def build(self):
            return Button(text='Open Web',
                          on_release=self.open_web)

        @staticmethod
        def open_web():
            browser = webbrowser.get(web_name)
            browser.open('https://ordereat.co')


    TestApp().run()
