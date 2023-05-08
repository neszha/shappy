package com.neszha.sheppy

import android.annotation.SuppressLint
import android.os.Bundle
import android.view.MotionEvent
import android.view.View
import android.webkit.*
import android.widget.LinearLayout
import androidx.appcompat.app.AppCompatActivity
import androidx.swiperefreshlayout.widget.SwipeRefreshLayout
import androidx.swiperefreshlayout.widget.SwipeRefreshLayout.OnRefreshListener
import kotlinx.coroutines.*

class MainActivity : AppCompatActivity(), OnRefreshListener {

    private var webView: WebView? = null
    private var webViewLoaded: Boolean = false
    private var refreshLayout: SwipeRefreshLayout? = null

    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)
        this.setContentView(R.layout.activity_main)
        this.setupWebView()
    }

    override fun onResume() {
        super.onResume()
        if(webViewLoaded) {
            recreate()
        }
    }

    override fun onRefresh() {
        refreshLayout!!.isRefreshing = true
        webView!!.reload()
        CoroutineScope(Dispatchers.Default).launch {
            delay(2500)
            refreshLayout!!.isRefreshing = false
        }
    }

    override fun onStop() {
        super.onStop()
        webView!!.destroy()
    }

    @SuppressLint("SetJavaScriptEnabled", "ClickableViewAccessibility")
    private fun setupWebView() {
        val webviewLoaderWrapper = findViewById<LinearLayout>(R.id.webview_loader)
        webView = findViewById(R.id.webview)
        refreshLayout = findViewById(R.id.swiperefresh)

        // Setup web-view.
        webView!!.webViewClient = object : WebViewClient() {
            override fun onPageFinished(view: WebView?, url: String?) {
                super.onPageFinished(view, url)
                webviewLoaderWrapper.visibility = View.GONE
                webViewLoaded = true
            }
        }

        // Web view settings.
        val webSettings = webView!!.settings
        webSettings.javaScriptEnabled = true
        webSettings.domStorageEnabled = true

        // Open endpoint.
        webView!!.loadUrl(Store.webViewBaseLink)

        // Handle swipe refresh.
        refreshLayout!!.isEnabled = false
        refreshLayout!!.setOnRefreshListener(this)

        webView!!.setOnTouchListener { _, event ->
            if (event?.action == MotionEvent.ACTION_DOWN) {
                refreshLayout!!.isEnabled = event.y <= 200
            }
            false
        }
    }
}