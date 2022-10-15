package kz.zhakhanyergali.qrscanner.Activity;

import android.app.ProgressDialog;
import android.content.Intent;
import android.support.v7.app.AppCompatActivity;
import android.os.Bundle;
import android.util.Log;
import android.view.View;
import android.widget.Button;
import android.widget.EditText;
import android.widget.Toast;

import com.android.volley.Response;
import com.android.volley.VolleyError;
import com.android.volley.toolbox.JsonObjectRequest;
import com.android.volley.toolbox.Volley;

import org.json.JSONException;
import org.json.JSONObject;

import java.util.HashMap;


import kz.zhakhanyergali.qrscanner.R;
import kz.zhakhanyergali.qrscanner.SQLite.ORM.AppItemORM;

public class LoginActivity extends AppCompatActivity {

    EditText password;
    Button login;
    EditText username;
    ProgressDialog progressDialog;
    AppItemORM appItemORM;

    @Override
    protected void onCreate(Bundle savedInstanceState) {
        super.onCreate(savedInstanceState);
        setContentView(R.layout.activity_login);
        login = findViewById(R.id.login_login);
        password = findViewById(R.id.login_password);
        username = findViewById(R.id.login_username);
        appItemORM = new AppItemORM();

        String seller_token = appItemORM.get(this, "seller_token");
        login.setOnClickListener(new View.OnClickListener() {
            @Override
            public void onClick(View view) {
                send_req(null);
            }
        });
        if(seller_token != null){
            Log.e("HIIII", "Yes Seller token");
            send_req(seller_token);
        }

    }

    private void send_req(String token){

        enable_views(false);
        HashMap<String, String> params = new HashMap<String, String>();
        if(token==null){
            params.put("password", password.getText().toString());
            params.put("username", username.getText().toString());
        }
        else{
            params.put("seller_token", token);
        }
        progressDialog = ProgressDialog.show(this, "Logging in...", "Please wait...");
        JsonObjectRequest request_json = new JsonObjectRequest( getResources().getString(R.string.server_url) + "/login", new JSONObject(params),
                new Response.Listener<JSONObject>() {
                    @Override
                    public void onResponse(JSONObject response) {
                        progressDialog.dismiss();
                        enable_views(true);
                        Log.e("HIIII",response.toString());
                        try {
                            String seller_token = response.getString("seller_token");
                            String seller_name = response.getString("seller_name");
                            appItemORM.add(LoginActivity.this, "seller_token", seller_token);
                            appItemORM.add(LoginActivity.this, "seller_name", seller_name);
                            Toast.makeText(LoginActivity.this, "Logged in as "+seller_name, Toast.LENGTH_LONG).show();
                            Intent intent = new Intent(LoginActivity.this, MainActivity.class);
                            startActivity(intent);
                            finish();
                        } catch (JSONException e) {
                            System.exit(0);
                        }
                    }
                }, new Response.ErrorListener() {
            @Override
            public void onErrorResponse(VolleyError volleyError) {
                progressDialog.dismiss();
                enable_views(true);
                if(volleyError.networkResponse == null){
                    Toast.makeText(LoginActivity.this, "Network connection error.", Toast.LENGTH_LONG).show();
                }
                else{
                    if(volleyError.networkResponse.statusCode == 400){
                        Toast.makeText(LoginActivity.this, "Token expired. Please re-login.", Toast.LENGTH_LONG).show();
                    }
                    else{
                        Toast.makeText(LoginActivity.this, "Invalid credential.", Toast.LENGTH_LONG).show();
                    }
                }
            }
        });
        Volley.newRequestQueue(this).add(request_json);
    }

    private void enable_views(boolean enable){
        username.setEnabled(enable);
        password.setEnabled(enable);
        login.setEnabled(enable);
    }
}
