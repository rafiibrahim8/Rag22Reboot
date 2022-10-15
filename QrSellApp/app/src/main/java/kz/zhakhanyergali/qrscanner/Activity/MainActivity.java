package kz.zhakhanyergali.qrscanner.Activity;

import android.Manifest;
import android.app.ProgressDialog;
import android.content.Intent;
import android.content.pm.PackageManager;
import android.support.v4.app.ActivityCompat;
import android.support.v7.app.AppCompatActivity;
import android.os.Bundle;
import android.util.Log;
import android.view.View;
import android.view.ViewGroup;
import android.widget.ImageView;
import android.widget.TextView;
import android.widget.Toast;

import com.android.volley.Response;
import com.android.volley.VolleyError;
import com.android.volley.toolbox.JsonObjectRequest;
import com.android.volley.toolbox.Volley;
import com.google.zxing.BarcodeFormat;
import com.google.zxing.Result;

import org.json.JSONException;
import org.json.JSONObject;

import java.util.ArrayList;
import java.util.Arrays;
import java.util.HashMap;

import kz.zhakhanyergali.qrscanner.R;
import kz.zhakhanyergali.qrscanner.SQLite.ORM.AppItemORM;
import me.dm7.barcodescanner.zxing.ZXingScannerView;

public class MainActivity extends AppCompatActivity implements ZXingScannerView.ResultHandler {

    // Init ui elements
    ImageView flashImageView;
    TextView seller_name;
    ProgressDialog progressDialog;

    AppItemORM appItemORM;
    private ZXingScannerView mScannerView;


    @Override
    protected void onCreate(Bundle savedInstanceState) {
        super.onCreate(savedInstanceState);
        setContentView(R.layout.activity_main);
        flashImageView = findViewById(R.id.lightButton);
        seller_name = findViewById(R.id.ma_seller_name);

        appItemORM = new AppItemORM();
        seller_name.setText("Hello, " + appItemORM.get(this, "seller_name"));

        ActivityCompat.requestPermissions(MainActivity.this,
                new String[]{Manifest.permission.CAMERA},
                1);

        ViewGroup contentFrame = (ViewGroup) findViewById(R.id.content_frame);
        mScannerView = new ZXingScannerView(this);
        mScannerView.setFormats(new ArrayList<>(Arrays.asList(BarcodeFormat.QR_CODE)));
        contentFrame.addView(mScannerView);
        flashImageView.setOnClickListener(new View.OnClickListener() {
            @Override
            public void onClick(View view) {
                boolean flash = mScannerView.getFlash();
                if(flash){
                    flashImageView.setBackgroundResource(R.drawable.ic_flash_on);
                    mScannerView.setFlash(false);
                }
                else {
                    flashImageView.setBackgroundResource(R.drawable.ic_flash_off);
                    mScannerView.setFlash(true);
                }
            }
        });
    }

    @Override
    public void onResume() {
        super.onResume();
        mScannerView.setResultHandler(this);
        mScannerView.startCamera();
    }

    @Override
    public void onPause() {
        super.onPause();
        mScannerView.stopCamera();
    }

    @Override
    public void handleResult(final Result rawResult) {
        String qrText = rawResult.getText();
        if(!qrText.startsWith(getResources().getString(R.string.qr_prefix))){
            mScannerView.resumeCameraPreview(this);
            return;
        }
        send_req(qrText);
    }

    private void send_req(String qrText){

        HashMap<String, String> params = new HashMap<String, String>();
        params.put("qr_text", qrText);
        params.put("seller_token", appItemORM.get(this, "seller_token"));

        progressDialog = ProgressDialog.show(this, "Validating QR...", "Please wait...");
        JsonObjectRequest request_json = new JsonObjectRequest(getResources().getString(R.string.server_url) + "/qr_scan", new JSONObject(params),
                new Response.Listener<JSONObject>() {
                    @Override
                    public void onResponse(JSONObject response) {
                        progressDialog.dismiss();
                        Log.e("HIIII",response.toString());
                        try {
                            String customer_name = response.getString("customer_name");
                            String customer_phone = response.getString("customer_phone");
                            String customer_amount = response.getString("customer_amount");
                            String qrid = response.getString("qrid");
                            String qr_text = response.getString("qr_text");
                            Boolean customer_is_edit = response.getBoolean("customer_is_edit");
                            Boolean editable = response.getBoolean("editable");
                            String extra_text =  response.getString("extra_text");

                            Intent intent = new Intent(MainActivity.this, DataEntryActivity.class);
                            intent.putExtra("customer_name", customer_name);
                            intent.putExtra("customer_phone", customer_phone);
                            intent.putExtra("customer_amount", customer_amount);
                            intent.putExtra("qrid", qrid);
                            intent.putExtra("customer_is_edit", customer_is_edit);
                            intent.putExtra("qr_text", qr_text);
                            intent.putExtra("extra_text", extra_text);
                            intent.putExtra("editable", editable);
                            startActivity(intent);
                        } catch (JSONException e) {
                            System.exit(0);
                        }
                    }
                }, new Response.ErrorListener() {
            @Override
            public void onErrorResponse(VolleyError volleyError) {
                progressDialog.dismiss();
                if(volleyError.networkResponse == null){
                    Toast.makeText(MainActivity.this, "Network connection error.", Toast.LENGTH_SHORT).show();
                    mScannerView.resumeCameraPreview(MainActivity.this);
                }
                else if(volleyError.networkResponse.statusCode == 401){
                    startActivity(new Intent(MainActivity.this, NotSoldActivity.class));
                    // Toast.makeText(MainActivity.this, "This t-shirt was not sold.", Toast.LENGTH_SHORT).show();
                    // mScannerView.resumeCameraPreview(MainActivity.this);
                }
                else{
                    Toast.makeText(MainActivity.this, "Counterfeit QR code.", Toast.LENGTH_SHORT).show();
                    mScannerView.resumeCameraPreview(MainActivity.this);
                }
            }
        });
        Volley.newRequestQueue(this).add(request_json);
    }

    @Override
    public void onRequestPermissionsResult(int requestCode, String permissions[], int[] grantResults) {
        switch (requestCode) {
            case 1: {
                if (grantResults.length > 0
                        && grantResults[0] == PackageManager.PERMISSION_GRANTED) {
                } else {
                    Toast.makeText(MainActivity.this, "Permission denied to camera", Toast.LENGTH_SHORT).show();
                }
                return;
            }
        }
    }
}
