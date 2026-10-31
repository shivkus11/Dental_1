package com.example.dentalclinic;

import android.app.Activity;
import android.os.Bundle;
import android.os.StrictMode;
import android.graphics.Typeface;
import android.view.Gravity;
import android.view.View;
import android.widget.*;
import org.json.JSONArray;
import org.json.JSONObject;

public class MainActivity extends Activity {
    LinearLayout root, content;
    EditText username, password;
    int pad=24;

    @Override public void onCreate(Bundle saved) {
        super.onCreate(saved);
        StrictMode.setThreadPolicy(new StrictMode.ThreadPolicy.Builder().permitAll().build());
        showLogin();
    }

    TextView text(String s, int size) {
        TextView t=new TextView(this); t.setText(s); t.setTextSize(size); t.setTextColor(0xFF173B57);
        t.setPadding(0,8,0,8); return t;
    }
    EditText field(String hint) {
        EditText e=new EditText(this); e.setHint(hint); e.setSingleLine(false);
        e.setPadding(14,10,14,10); return e;
    }
    Button button(String label, Runnable action) {
        Button b=new Button(this); b.setText(label); b.setOnClickListener(v->action.run()); return b;
    }
    void base(String title) {
        root=new LinearLayout(this); root.setOrientation(LinearLayout.VERTICAL); root.setPadding(pad,pad,pad,pad);
        root.setBackgroundColor(0xFFF3F7FA);
        TextView h=text(title,24); h.setTypeface(null,Typeface.BOLD); root.addView(h);
        ScrollView sc=new ScrollView(this); content=new LinearLayout(this); content.setOrientation(LinearLayout.VERTICAL);
        sc.addView(content); root.addView(sc,new LinearLayout.LayoutParams(-1,0,1));
        setContentView(root);
    }
    void message(String s) { Toast.makeText(this,s,Toast.LENGTH_LONG).show(); }
    void showLogin() {
        base("Dental Clinic Management");
        content.addView(text("Sign in to shared clinic records",16));
        username=field("Username"); username.setText("admin"); content.addView(username);
        password=field("Password"); password.setInputType(129); password.setText("ChangeMe123!"); content.addView(password);
        content.addView(button("Login",()->login()));
        content.addView(text("Make sure the Flask backend is running on your PC.",14));
    }
    void login() {
        try {
            JSONObject d=new JSONObject(); d.put("username",username.getText().toString().trim()); d.put("password",password.getText().toString());
            ApiClient.request("login","POST",d); showHome();
        } catch(Exception e) { message(e.getMessage()); }
    }
    void showHome() {
        base("Dental Clinic");
        content.addView(text("Shared database · Android + browser",14));
        content.addView(button("Dashboard",()->loadDashboard()));
        content.addView(button("Register patient",()->patientForm()));
        content.addView(button("Search patients",()->searchPatients()));
        content.addView(button("Add treatment",()->treatmentForm()));
        content.addView(button("Schedule appointment",()->appointmentForm()));
        content.addView(button("Follow-up",()->followupForm()));
        content.addView(button("Refresh appointments",()->loadAppointments()));
        content.addView(button("Log out",()->{try{ApiClient.request("logout","POST",new JSONObject());}catch(Exception ignored){}showLogin();}));
        loadDashboard();
    }
    void clearContent(){content.removeAllViews();}
    void loadDashboard() {
        clearContent();
        content.addView(text("Clinic dashboard",20));
        try {
            JSONObject d=ApiClient.request("dashboard","GET",null);
            content.addView(text("Patients: "+d.optInt("patients")+"\nScheduled appointments: "+d.optInt("appointments")+
                    "\nTreatments: "+d.optInt("treatments")+"\nPending follow-ups: "+d.optInt("followups"),17));
        } catch(Exception e){content.addView(text(e.getMessage(),14));}
        content.addView(button("Register patient",()->patientForm()));
        content.addView(button("Search patients",()->searchPatients()));
    }
    void patientForm() {
        clearContent(); content.addView(text("Patient registration",20));
        EditText name=field("Full name *"), dob=field("Date of birth YYYY-MM-DD"), gender=field("Gender"), phone=field("Phone"),
            email=field("Email"), address=field("Address"), emergency=field("Emergency contact");
        content.addView(name);content.addView(dob);content.addView(gender);content.addView(phone);content.addView(email);content.addView(address);content.addView(emergency);
        content.addView(button("Save patient",()->{
            try {
                JSONObject d=new JSONObject();d.put("full_name",name.getText().toString().trim());d.put("dob",dob.getText().toString());
                d.put("gender",gender.getText().toString());d.put("phone",phone.getText().toString());d.put("email",email.getText().toString());
                d.put("address",address.getText().toString());d.put("emergency_contact",emergency.getText().toString());
                JSONObject r=ApiClient.request("patients","POST",d);
                message("Saved patient ID "+r.optInt("id")+" · "+r.optString("patient_code")); showHome();
            }catch(Exception e){message(e.getMessage());}
        }));
        content.addView(button("Back",()->showHome()));
    }
    void searchPatients() {
        clearContent(); content.addView(text("Search patients",20));
        EditText q=field("Name, patient code or phone");content.addView(q);
        content.addView(button("Search",()->{
            try {
                JSONArray a=ApiClient.getArray("patients?q="+java.net.URLEncoder.encode(q.getText().toString(),"UTF-8"));
                clearContent();content.addView(text("Search results",20));
                for(int i=0;i<a.length();i++){
                    JSONObject p=a.getJSONObject(i);
                    content.addView(text(p.optString("full_name")+" · "+p.optString("patient_code")+
                            "\nID: "+p.optInt("id")+" · "+p.optString("phone"),16));
                    int id=p.optInt("id");
                    content.addView(button("Open patient summary",()->patientSummary(id)));
                }
                content.addView(button("Back",()->showHome()));
            }catch(Exception e){message(e.getMessage());}
        }));
        content.addView(button("Back",()->showHome()));
    }
    void patientSummary(int id) {
        clearContent();
        try {
            JSONObject d=ApiClient.request("patients/"+id,"GET",null);
            JSONObject p=d.getJSONObject("patient"), m=d.optJSONObject("medical_history");
            content.addView(text(p.optString("full_name")+" ("+p.optString("patient_code")+")",20));
            content.addView(text("DOB: "+p.optString("dob")+"\nPhone: "+p.optString("phone")+
                    "\nConditions: "+m.optString("conditions")+"\nAllergies: "+m.optString("allergies")+
                    "\nMedications: "+m.optString("medications"),16));
            content.addView(text("Treatments: "+d.getJSONArray("treatments").length()+
                    "\nAppointments: "+d.getJSONArray("appointments").length()+
                    "\nImages: "+d.getJSONArray("images").length()+
                    "\nFollow-ups: "+d.getJSONArray("followups").length(),16));
        }catch(Exception e){message(e.getMessage());}
        content.addView(button("Back to search",()->searchPatients()));
    }
    void treatmentForm() {
        clearContent();content.addView(text("Dental treatment",20));
        EditText pid=field("Patient ID *"), category=field("Category (use exact category name)"), tooth=field("Tooth number"),
                date=field("Treatment date YYYY-MM-DD"), cost=field("Cost"), status=field("Status: Planned / In progress / Completed"), desc=field("Description");
        content.addView(pid);content.addView(category);content.addView(tooth);content.addView(date);content.addView(cost);content.addView(status);content.addView(desc);
        content.addView(text("Categories: X-rays, Implants, Tooth extraction, Caries filling, Missing teeth, Bridges, Crowns, Removable partial dentures (RPD), Periodontitis treatment, Scaling",13));
        content.addView(button("Save treatment",()->{
            try{JSONObject d=new JSONObject();d.put("patient_id",Integer.parseInt(pid.getText().toString()));d.put("category",category.getText().toString());
                d.put("tooth_number",tooth.getText().toString());d.put("treatment_date",date.getText().toString());d.put("cost",cost.getText().length()==0?0:Double.parseDouble(cost.getText().toString()));
                d.put("status",status.getText().length()==0?"Planned":status.getText().toString());d.put("description",desc.getText().toString());
                ApiClient.request("treatments","POST",d);message("Treatment saved");showHome();
            }catch(Exception e){message(e.getMessage());}
        }));
        content.addView(button("Back",()->showHome()));
    }
    void appointmentForm() {
        clearContent();content.addView(text("Schedule appointment",20));
        EditText pid=field("Patient ID *"), at=field("Date/time YYYY-MM-DDTHH:MM"), doctor=field("Doctor"), reason=field("Reason");
        content.addView(pid);content.addView(at);content.addView(doctor);content.addView(reason);
        content.addView(button("Save appointment",()->{
            try{JSONObject d=new JSONObject();d.put("patient_id",Integer.parseInt(pid.getText().toString()));d.put("appointment_at",at.getText().toString());
                d.put("doctor",doctor.getText().toString());d.put("reason",reason.getText().toString());ApiClient.request("appointments","POST",d);message("Appointment scheduled");showHome();
            }catch(Exception e){message(e.getMessage());}
        }));
        content.addView(button("Back",()->showHome()));
    }
    void followupForm() {
        clearContent();content.addView(text("Add follow-up",20));
        EditText pid=field("Patient ID *"), date=field("Due date YYYY-MM-DD"), notes=field("Notes");
        content.addView(pid);content.addView(date);content.addView(notes);
        content.addView(button("Save follow-up",()->{
            try{JSONObject d=new JSONObject();d.put("patient_id",Integer.parseInt(pid.getText().toString()));d.put("due_date",date.getText().toString());d.put("notes",notes.getText().toString());
                ApiClient.request("followups","POST",d);message("Follow-up saved");showHome();
            }catch(Exception e){message(e.getMessage());}
        }));
        content.addView(button("Back",()->showHome()));
    }
    void loadAppointments() {
        clearContent();content.addView(text("Appointments",20));
        try{JSONArray a=ApiClient.getArray("appointments");for(int i=0;i<a.length();i++){JSONObject x=a.getJSONObject(i);
            content.addView(text(x.optString("full_name")+" · "+x.optString("appointment_at")+"\n"+x.optString("status")+" · "+x.optString("reason"),15));
        }}catch(Exception e){content.addView(text(e.getMessage(),14));}
        content.addView(button("Back",()->showHome()));
    }
}
