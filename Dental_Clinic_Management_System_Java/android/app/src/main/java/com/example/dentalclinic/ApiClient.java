package com.example.dentalclinic;

import org.json.JSONObject;
import org.json.JSONArray;
import java.io.*;
import java.net.HttpURLConnection;
import java.net.URL;

public class ApiClient {
    // Android emulator -> host PC. For a physical device, use http://YOUR_PC_LAN_IP:5000/api/
    public static String BASE_URL = "http://10.0.2.2:5000/api/";
    private static String cookie = "";

    public static JSONObject request(String path, String method, JSONObject payload) throws Exception {
        HttpURLConnection conn = (HttpURLConnection) new URL(BASE_URL + path).openConnection();
        conn.setRequestMethod(method);
        conn.setConnectTimeout(8000);
        conn.setReadTimeout(8000);
        conn.setRequestProperty("Accept", "application/json");
        if (!cookie.isEmpty()) conn.setRequestProperty("Cookie", cookie);
        if (payload != null) {
            conn.setDoOutput(true);
            conn.setRequestProperty("Content-Type", "application/json; charset=UTF-8");
            try (OutputStream os = conn.getOutputStream()) {
                os.write(payload.toString().getBytes("UTF-8"));
            }
        }
        String setCookie = conn.getHeaderField("Set-Cookie");
        if (setCookie != null) cookie = setCookie.split(";", 2)[0];
        int code = conn.getResponseCode();
        InputStream is = (code >= 200 && code < 400) ? conn.getInputStream() : conn.getErrorStream();
        ByteArrayOutputStream out = new ByteArrayOutputStream();
        if (is != null) { byte[] b = new byte[4096]; int n; while ((n=is.read(b))!=-1) out.write(b,0,n); is.close(); }
        conn.disconnect();
        String text = out.toString("UTF-8");
        if (code < 200 || code >= 300) throw new Exception("HTTP " + code + ": " + text);
        return new JSONObject(text);
    }

    public static JSONArray getArray(String path) throws Exception {
        HttpURLConnection conn = (HttpURLConnection) new URL(BASE_URL + path).openConnection();
        conn.setRequestMethod("GET");
        conn.setConnectTimeout(8000); conn.setReadTimeout(8000);
        if (!cookie.isEmpty()) conn.setRequestProperty("Cookie", cookie);
        int code=conn.getResponseCode();
        InputStream is=(code>=200&&code<400)?conn.getInputStream():conn.getErrorStream();
        ByteArrayOutputStream out=new ByteArrayOutputStream();
        if(is!=null){byte[] b=new byte[4096];int n;while((n=is.read(b))!=-1)out.write(b,0,n);is.close();}
        conn.disconnect();
        String text=out.toString("UTF-8");
        if(code<200||code>=300)throw new Exception("HTTP "+code+": "+text);
        return new JSONArray(text);
    }
}
