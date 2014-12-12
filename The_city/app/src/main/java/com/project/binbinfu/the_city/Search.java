package com.project.binbinfu.the_city;


import android.app.ActionBar;
import android.app.Activity;
import android.content.Context;
import android.os.AsyncTask;
import android.preference.EditTextPreference;
import android.widget.AdapterView.OnItemClickListener;

import com.google.gson.Gson;
import com.google.gson.GsonBuilder;
import com.loopj.android.http.AsyncHttpClient;
import com.loopj.android.http.JsonHttpResponseHandler;


import android.os.Bundle;
import android.support.v7.app.ActionBarActivity;
import android.util.Log;
import android.view.View;
import android.widget.AdapterView;
import android.widget.ArrayAdapter;
import android.widget.Button;
import android.widget.EditText;
import android.widget.TextView;
import android.widget.Toast;

import org.apache.http.HttpEntity;
import org.apache.http.HttpResponse;
import org.apache.http.StatusLine;
import org.apache.http.client.HttpClient;
import org.apache.http.client.methods.HttpPost;
import org.apache.http.entity.StringEntity;
import org.apache.http.impl.client.DefaultHttpClient;
import org.apache.http.message.BasicHeader;
import org.apache.http.protocol.HTTP;
import org.json.JSONException;
import org.json.JSONObject;


import java.io.InputStream;
import java.io.InputStreamReader;
import java.io.Reader;
import java.io.UnsupportedEncodingException;
import java.util.ArrayList;
import java.util.Collections;
import java.util.List;

import org.apache.http.Header;


public class Search extends Activity implements View.OnClickListener{
    private static ImageAdapter adapter ;
    private Search_streams streams;
    String[] types_actionbar = new String[]{
            "All",
            "Music",
            "Food",
            "Movie",
            "Travel",
            "Party",
            "Reading"
    };

    @Override
    protected void onCreate(Bundle savedInstanceState) {
        super.onCreate(savedInstanceState);
        setContentView(R.layout.activity_search);
        /** Create an array adapter to populate dropdownlist */
        ArrayAdapter<String> adapter1 = new ArrayAdapter<String>(getBaseContext(), android.R.layout.simple_spinner_dropdown_item, types_actionbar);
        /** Enabling dropdown list navigation for the action bar */
        //getActionBar().setBackgroundDrawable(getResources().getDrawable(R.drawable.abc_ab_share_pack_holo_light));
        //getActionBar().setDisplayShowTitleEnabled(true);
        //getActionBar().setDisplayShowTitleEnabled(false);
        getActionBar().setNavigationMode(ActionBar.NAVIGATION_MODE_LIST);
        /** Defining Navigation listener */
        ActionBar.OnNavigationListener navigationListener = new ActionBar.OnNavigationListener() {


            @Override
            public boolean onNavigationItemSelected(int itemPosition, long itemId) {
                Log.v("ann","droplist");
                Toast.makeText(getBaseContext(), "You selected : " + types_actionbar[itemPosition]  , Toast.LENGTH_SHORT).show();
                if(adapter == null) {
                    Log.v("ann","null");
                    return false;

                }
                else{
                    if(types_actionbar[itemPosition].equals("All")){
                        adapter.covers.clear();
                        adapter.ids.clear();
                        adapter.titles.clear();
                        adapter.starts.clear();
                        adapter.ends.clear();
                        adapter.locations.clear();
                        adapter.types.clear();
                        if (!streams.ongoing_activity.isEmpty()) {
                            Log.v("ann", "ongoing_not_empty");
                            adapter.covers.addAll(streams.ongoing_cover);
                            adapter.ids.addAll(streams.ongoing_activity);
                            adapter.titles.addAll(streams.ongoing_title);
                            adapter.starts.addAll(streams.ongoing_start_time);
                            adapter.ends.addAll(streams.ongoing_end_time);
                            adapter.locations.addAll(streams.ongoing_location);
                            adapter.types.addAll(streams.ongoing_tag);
                        }
                        if (!streams.past_activity.isEmpty()) {
                            Log.v("ann", "past_notempty");
                            adapter.covers.addAll(streams.past_cover);
                            adapter.ids.addAll(streams.past_activity);
                            adapter.titles.addAll(streams.past_title);
                            adapter.starts.addAll(streams.past_start_time);
                            adapter.ends.addAll(streams.past_end_time);
                            adapter.locations.addAll(streams.past_location);
                            adapter.types.addAll(streams.past_tag);

                        }
                        adapter.notifyDataSetChanged();
                        final ExpandableGridView gridview = (ExpandableGridView)findViewById(R.id.grid_view);
                        gridview.setAdapter(adapter);
                        return true;

                    }
                    List<String> covers = new ArrayList<String>();
                    List<String> ids = new ArrayList<String>();
                    List<String> titles = new ArrayList<String>();
                    List<String> starts = new ArrayList<String>();
                    List<String> ends = new ArrayList<String>();
                    List<String> locations = new ArrayList<String>();
                    List<String> types = new ArrayList<String>();
                    for(int i = 0; i<streams.ongoing_tag.size();i++){
                        if (streams.ongoing_tag.get(i).equalsIgnoreCase(types_actionbar[itemPosition])){
                            covers.add(streams.ongoing_cover.get(i));
                            ids.add(streams.ongoing_activity.get(i));
                            titles.add(streams.ongoing_title.get(i));
                            starts.add(streams.ongoing_start_time.get(i));
                            ends.add(streams.ongoing_end_time.get(i));
                            locations.add(streams.ongoing_location.get(i));
                            types.add(streams.ongoing_tag.get(i));

                        }
                    }
                    for(int i = 0; i<streams.past_tag.size();i++){
                        if (streams.past_tag.get(i).equalsIgnoreCase(types_actionbar[itemPosition])){
                            covers.add(streams.past_cover.get(i));
                            ids.add(streams.past_activity.get(i));
                            titles.add(streams.past_title.get(i));
                            starts.add(streams.past_start_time.get(i));
                            ends.add(streams.past_end_time.get(i));
                            locations.add(streams.past_location.get(i));
                            types.add(streams.past_tag.get(i));
                        }
                    }
                    adapter.covers.clear();
                    adapter.covers.addAll(covers);
                    adapter.ids.clear();
                    adapter.ids.addAll(ids);
                    adapter.titles.clear();
                    adapter.titles.addAll(titles);
                    adapter.starts.clear();
                    adapter.starts.addAll(starts);
                    adapter.ends.clear();
                    adapter.ends.addAll(ends);
                    adapter.locations.clear();
                    adapter.locations.addAll(locations);
                    adapter.types.clear();
                    adapter.types.addAll(types);
                    adapter.notifyDataSetChanged();
                    final ExpandableGridView gridview = (ExpandableGridView)findViewById(R.id.grid_view);
                    gridview.setAdapter(adapter);
                    return true;

                }

            }
        };

        /** Setting dropdown items and item navigation listener for the actionbar */
        getActionBar().setListNavigationCallbacks(adapter1, navigationListener);


        Button search = (Button) findViewById(R.id.search_button);
        search.setOnClickListener(this);
        PostFetcher fetcher = new PostFetcher();
        fetcher.execute();
        /*
        Gridview onclicklistener
         */
        final ExpandableGridView gridview = (ExpandableGridView)findViewById(R.id.grid_view);
        gridview.setOnItemClickListener(new OnItemClickListener() {
            public void onItemClick(AdapterView<?> parent, View v, int position, long id) {
                //Bundle bundle = new Bundle();
                //bundle.putString("id", Long.toString(id));
                //bundle.putString("name", adapter.names.get(position));
                //Intent intent = new Intent(Viewall.this, Viewone.class);
                //intent.putExtras(bundle);
                //Search.this.startActivity(intent);
                //Toast.makeText(rootView.getContext(), "" + id, Toast.LENGTH_SHORT).show();
            }
        });
    }

    @Override
    public void onClick(View view){
        switch(view.getId()){
            case R.id.search_button:
                Log.v("ann","press button");
                final EditText keyword = (EditText) findViewById(R.id.keyword);
                if (keyword.getText().toString().equals("")) {
                    Toast.makeText(Search.this, "Please enter the keyword", Toast.LENGTH_SHORT).show();
                    PostFetcher post = new PostFetcher();
                    post.execute();
                    Log.v("ann","no keyword");
                }
                else{
                    String key = keyword.getText().toString();
                    Log.v("ann", "get keyword");
                    Log.v("ann",key);
                    AsyncHttpClient client = new AsyncHttpClient();
                    JSONObject jsonObject = new JSONObject();
                    StringEntity entity = null;
                    try {
                        jsonObject.put("keyword", key);
                        entity = new StringEntity(jsonObject.toString());
                        entity.setContentType(new BasicHeader(HTTP.CONTENT_TYPE, "application/json"));
                    } catch (JSONException e) {
                        Log.v("ann", e.getMessage());
                    } catch (UnsupportedEncodingException e) {
                        Log.v("ann", e.getMessage());
                    }
                    Log.v("ann","before_send");
                    client.post(view.getContext(), "http://helloworld0923.appspot.com/api/search", entity, "application/json", new JsonHttpResponseHandler() {
                        public void onSuccess(int statusCode, Header[] headers, JSONObject response) {
                            try {
                                Log.v("ann", "onSuccess");
                                GsonBuilder gsonBuilder = new GsonBuilder();
                                Gson gson = gsonBuilder.create();
                                String str = response.toString();
                                Log.v("ann", str);
                                streams = gson.fromJson(str, Search_streams.class);
                                if(adapter == null)
                                    adapter = new ImageAdapter(Search.this, new ArrayList<String>(), new ArrayList<String>(), new ArrayList<String>(),
                                            new ArrayList<String>(), new ArrayList<String>(), new ArrayList<String>(), new ArrayList<String>());
                                adapter.covers.clear();
                                adapter.ids.clear();
                                adapter.titles.clear();
                                adapter.starts.clear();
                                adapter.ends.clear();
                                adapter.locations.clear();
                                adapter.types.clear();
                                if (!streams.ongoing_activity.isEmpty()) {
                                    Log.v("ann", "ongoing_not_empty");
                                    adapter.covers.addAll(streams.ongoing_cover);
                                    adapter.ids.addAll(streams.ongoing_activity);
                                    adapter.titles.addAll(streams.ongoing_title);
                                    adapter.starts.addAll(streams.ongoing_start_time);
                                    adapter.ends.addAll(streams.ongoing_end_time);
                                    adapter.locations.addAll(streams.ongoing_location);
                                    adapter.types.addAll(streams.ongoing_tag);
                                }
                                if (!streams.past_activity.isEmpty()) {
                                    Log.v("ann", "past_notempty");
                                    adapter.covers.addAll(streams.past_cover);
                                    adapter.ids.addAll(streams.past_activity);
                                    adapter.titles.addAll(streams.past_title);
                                    adapter.starts.addAll(streams.past_start_time);
                                    adapter.ends.addAll(streams.past_end_time);
                                    adapter.locations.addAll(streams.past_location);
                                    adapter.types.addAll(streams.past_tag);

                                }
                                adapter.notifyDataSetChanged();
                                final ExpandableGridView gridview = (ExpandableGridView)findViewById(R.id.grid_view);
                                gridview.setAdapter(adapter);
                            } catch (Exception ex) {
                                Log.v("ann", "Failed to parse JSON due to :" + ex);
                            }
                        }

                        @Override
                        public void onFailure(int statusCode, Header[] headers, Throwable throwable, JSONObject response) {
                            // Log.v("ann",response.toString());
                            Log.v("ann", "fail to request");
                            Log.v("ann", Long.toString(statusCode));

                        }
                    });
                }
                break;
        }
    }
    private void handlePostsList(){
        runOnUiThread(new Runnable() {
            @Override
            public void run() {
                if (adapter == null)
                    adapter = new ImageAdapter(Search.this, new ArrayList<String>(), new ArrayList<String>(),
                            new ArrayList<String>(), new ArrayList<String>(), new ArrayList<String>(), new ArrayList<String>(), new ArrayList<String>());
                adapter.covers.clear();
                adapter.ids.clear();
                adapter.titles.clear();
                adapter.starts.clear();
                adapter.ends.clear();
                adapter.locations.clear();
                adapter.types.clear();
                if (!streams.ongoing_activity.isEmpty()) {
                    Log.v("ann", "ongoing_not_empty");
                    adapter.covers.addAll(streams.ongoing_cover);
                    adapter.ids.addAll(streams.ongoing_activity);
                    adapter.titles.addAll(streams.ongoing_title);
                    adapter.starts.addAll(streams.ongoing_start_time);
                    adapter.ends.addAll(streams.ongoing_end_time);
                    adapter.locations.addAll(streams.ongoing_location);
                    adapter.types.addAll(streams.ongoing_tag);
                }
                if (!streams.past_activity.isEmpty()) {
                    Log.v("ann", "past_notempty");
                    adapter.covers.addAll(streams.past_cover);
                    adapter.ids.addAll(streams.past_activity);
                    adapter.titles.addAll(streams.past_title);
                    adapter.starts.addAll(streams.past_start_time);
                    adapter.ends.addAll(streams.past_end_time);
                    adapter.locations.addAll(streams.past_location);
                    adapter.types.addAll(streams.past_tag);

                }
                adapter.notifyDataSetChanged();
                final ExpandableGridView gridview = (ExpandableGridView)findViewById(R.id.grid_view);
                gridview.setAdapter(adapter);
            }
        });

    }

    private void failedLoadingPosts(){
        runOnUiThread(new Runnable(){
            @Override
        public void run(){
                Toast.makeText(Search.this, "Failed to load Posts",Toast.LENGTH_SHORT).show();
            }
        });
    }
    private class PostFetcher extends AsyncTask<Void, Void, String>{
        public static final String URL = "http://helloworld0923.appspot.com/api/get_all";

        @Override
        protected String doInBackground(Void... params){
            try{
                HttpClient client = new DefaultHttpClient();
                HttpPost post = new HttpPost(URL);

                HttpResponse response = client.execute(post);
                StatusLine statusLine = response.getStatusLine();
                if(statusLine.getStatusCode()==200){
                    HttpEntity entity = response.getEntity();
                    InputStream content = entity.getContent();
                    try{
                        Reader reader = new InputStreamReader(content);

                        GsonBuilder gsonBuilder = new GsonBuilder();
                        Gson gson = gsonBuilder.create();
                        streams = gson.fromJson(reader, Search_streams.class);

                        for(int i=0;i<streams.ongoing_activity.size();i++) {
                            content.close();
                        }
                        for(int i=0;i<streams.past_activity.size();i++)
                            content.close();
                        handlePostsList();
                    }catch (Exception ex){
                        Log.v("ann", "postfetcher "+"Failed to parse JSON due to: "+ex);
                    }
                }else{
                    Log.v("ann","Server responded with status code: "+statusLine.getStatusCode());
                    failedLoadingPosts();
                }
            }catch(Exception ex){
                Log.v("ann","postfetcher Failed to send HTTP POST request due to :"+ex);
            }
            return null;
        }
    }




}
