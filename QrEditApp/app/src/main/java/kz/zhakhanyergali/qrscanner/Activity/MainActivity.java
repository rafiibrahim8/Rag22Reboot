package kz.zhakhanyergali.qrscanner.Activity;

import android.app.ProgressDialog;
import android.content.Intent;
import android.support.v7.app.AppCompatActivity;
import android.os.Bundle;
import android.util.Log;
import android.view.View;
import android.widget.Button;
import android.widget.EditText;
import android.widget.TextView;
import android.widget.Toast;

import com.android.volley.Response;
import com.android.volley.VolleyError;
import com.android.volley.toolbox.JsonObjectRequest;
import com.android.volley.toolbox.Volley;

import org.json.JSONException;
import org.json.JSONObject;

import java.util.HashMap;
import java.util.Locale;

import kz.zhakhanyergali.qrscanner.R;
import kz.zhakhanyergali.qrscanner.SQLite.ORM.AppItemORM;

public class MainActivity extends AppCompatActivity{

    // Init ui elements
    TextView seller_name;
    EditText qridEt;
    Button editBtn;
    ProgressDialog progressDialog;

    AppItemORM appItemORM;


    @Override
    protected void onCreate(Bundle savedInstanceState) {
        super.onCreate(savedInstanceState);
        setContentView(R.layout.activity_main);
        seller_name = findViewById(R.id.ma_seller_name);
        qridEt = findViewById(R.id.ma_qrid);
        editBtn = findViewById(R.id.ma_edit);

        appItemORM = new AppItemORM();
        seller_name.setText("Hello, " + appItemORM.get(this, "seller_name"));
        editBtn.setOnClickListener(new View.OnClickListener() {
            @Override
            public void onClick(View view) {
                String qrid_t = qridEt.getText().toString();
                if(qrid_t.replace(" ","").length()<6 || (!qrid_t.toUpperCase().startsWith("Q"))){
                    Toast.makeText(MainActivity.this, "Invalid QR serial. Must start with 'Q'", Toast.LENGTH_SHORT).show();
                    return;
                }
                send_req(qrid_t.replace(" ","").toUpperCase());
            }
        });
    }

    private void send_req(String qrid_t){

        HashMap<String, String> params = new HashMap<String, String>();
        params.put("qrid", qrid_t);
        params.put("type", "get_info");
        params.put("seller_token", appItemORM.get(this, "seller_token"));

        progressDialog = ProgressDialog.show(this, "Checking Sell...", "Please wait...");
        JsonObjectRequest request_json = new JsonObjectRequest(getResources().getString(R.string.server_url) + "/edit_sell", new JSONObject(params),
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

                            Intent intent = new Intent(MainActivity.this, DataEntryActivity.class);
                            intent.putExtra("customer_name", customer_name);
                            intent.putExtra("customer_phone", customer_phone);
                            intent.putExtra("customer_amount", customer_amount);
                            intent.putExtra("qrid", qrid);
                            intent.putExtra("customer_is_edit", true);
                            intent.putExtra("extra_text", "");
                            intent.putExtra("editable", true);
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
                }
                else if(volleyError.networkResponse.statusCode == 401){
                    Toast.makeText(MainActivity.this, "This t-shirt was not sold.", Toast.LENGTH_SHORT).show();
                }
                else if(volleyError.networkResponse.statusCode == 403){
                    Toast.makeText(MainActivity.this, "You don't have permission to edit.", Toast.LENGTH_SHORT).show();
                }
                else if(volleyError.networkResponse.statusCode == 400){
                    Toast.makeText(MainActivity.this, "Invalid request.", Toast.LENGTH_SHORT).show();
                }
                else{
                    Toast.makeText(MainActivity.this, "An unexpected error occurred.", Toast.LENGTH_SHORT).show();
                }
            }
        });
        Volley.newRequestQueue(this).add(request_json);
    }
}
