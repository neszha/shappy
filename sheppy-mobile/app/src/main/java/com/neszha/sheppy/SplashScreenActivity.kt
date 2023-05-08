package com.neszha.sheppy

import android.annotation.SuppressLint
import android.content.Intent
import androidx.appcompat.app.AppCompatActivity
import android.os.Bundle
import android.widget.TextView
import kotlinx.coroutines.CoroutineScope
import kotlinx.coroutines.Dispatchers
import kotlinx.coroutines.delay
import kotlinx.coroutines.launch

class SplashScreenActivity : AppCompatActivity() {
    @SuppressLint("SetTextI18n")
    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)
        this.setContentView(R.layout.activity_splash_screen)

        // Show app version in splash screen.
        val packageName = applicationContext.packageName
        val packageInfo = applicationContext.packageManager.getPackageInfo(packageName, 0)
        val versionName = packageInfo.versionName
        val textViewAppVersion = findViewById<TextView>(R.id.textViewAppVersion)
        textViewAppVersion.text = "Version $versionName"

        // To main activity.
        this.openMainActivity()
    }

    private fun openMainActivity() {
        CoroutineScope(Dispatchers.Default).launch {
            delay(1500)
            val intent = Intent(this@SplashScreenActivity, MainActivity::class.java)
            this@SplashScreenActivity.startActivity(intent)
            this@SplashScreenActivity.finish()
        }
    }
}