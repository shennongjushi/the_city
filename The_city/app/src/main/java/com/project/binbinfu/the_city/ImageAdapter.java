package com.project.binbinfu.the_city;

import android.content.Context;
import android.view.LayoutInflater;
import android.view.View;
import android.view.ViewGroup;
import android.widget.BaseAdapter;
import android.widget.ImageView;
import android.widget.TextView;

import com.squareup.picasso.Picasso;

import java.util.ArrayList;
import java.util.List;

/**
 * Created by annyan on 12/10/14.
 */
public class ImageAdapter extends BaseAdapter{
    private Context mContext;
    public List<String> covers = new ArrayList<String>();
    public List<String> ids = new ArrayList<String>();
    public List<String> titles = new ArrayList<String>();
    public List<String> starts = new ArrayList<String>();
    public List<String> ends = new ArrayList<String>();
    public List<String> locations = new ArrayList<String>();
    public List<String> types = new ArrayList<String>();

    public ImageAdapter(Context c, List<String> cover, List<String> id, List<String>title,List<String> start, List<String> end, List<String> location, List<String> type){
        this.mContext = c;
        this.titles.addAll(title);
        this.covers.addAll(cover);
        this.ids.addAll(id);
        this.starts.addAll(start);
        this.ends.addAll(end);
        this.locations.addAll(location);
        this.types.addAll(type);
    }
    @Override
    public int getCount() {
        return covers.size();
    }

    @Override
    public String getItem(int position) {
        return covers.get(position);
    }

    @Override
    public long getItemId(int position) {
        return Long.parseLong(ids.get(position));
    }
    public View getView(int position, View convertView, ViewGroup parent){
        ImageView image;
        TextView title;
        TextView time;
        TextView location;
        TextView type;
        View grid;
        LayoutInflater inflater = (LayoutInflater)mContext.getSystemService(Context.LAYOUT_INFLATER_SERVICE);
        if(convertView == null){
            grid = new View(mContext);
            grid = inflater.inflate(R.layout.grid_single,null);
            image = (ImageView)grid.findViewById(R.id.cover);
            title = (TextView)grid.findViewById(R.id.title);
            time = (TextView)grid.findViewById(R.id.time);
            location = (TextView) grid.findViewById(R.id.location);
            type = (TextView) grid.findViewById(R.id.type);
        }else{
            grid = (View) convertView;
            image = (ImageView)grid.findViewById(R.id.cover);
            title = (TextView)grid.findViewById(R.id.title);
            time = (TextView)grid.findViewById(R.id.time);
            location = (TextView) grid.findViewById(R.id.location);
            type = (TextView) grid.findViewById(R.id.type);
        }
        title.setText(titles.get(position));
        String this_time = "Time: "+starts.get(position)+" -- "+ends.get(position);
        time.setText(this_time);
        location.setText("Location: "+locations.get(position));
        type.setText("Type: "+types.get(position));

        String url = "http://helloworld0923.appspot.com/img?key="+getItem(position);
        Picasso.with(mContext)
                .load(url)
                .placeholder(R.drawable.ico_loading)
                .resize(120,150)
                .into(image);

        return grid;

    }
}
