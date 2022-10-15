package kz.zhakhanyergali.qrscanner.SQLite.ORM;

import android.content.Context;
import android.database.Cursor;
import android.database.sqlite.SQLiteDatabase;
import android.util.Log;

import java.util.ArrayList;
import java.util.List;

import kz.zhakhanyergali.qrscanner.Entity.AppItem;
import kz.zhakhanyergali.qrscanner.SQLite.DatabaseWrapper;

public class AppItemORM implements InterfaceORM<AppItem>{
    public static final String TAG = "AppItemORM";

    public static final String COLUMN_NAME = "name";
    private static final String COMMA_SEPARATOR = ", ";
    public static final String COLUMN_NAME_TYPE = "TEXT PRIMARY KEY";
    public static final String COLUMN_VALUE_TYPE = "TEXT";
    public static final String COLUMN_VALUE = "value";
    public static final String TABLE_NAME = "app_items";
    public static final String SQL_DROP_TABLE = "DROP TABLE IF EXISTS " + TABLE_NAME;

    public static final String SQL_CREATE_TABLE = "CREATE TABLE " + TABLE_NAME + " (" +
            COLUMN_NAME + " " + COLUMN_NAME_TYPE + COMMA_SEPARATOR +
            COLUMN_VALUE + " " + COLUMN_VALUE_TYPE + ")";


    @Override
    public AppItem cursorToObject(Cursor cursor) {
        cursor.moveToFirst();
        return new AppItem(cursor.getString(cursor.getColumnIndex(COLUMN_NAME)),
                cursor.getString(cursor.getColumnIndex(COLUMN_VALUE)));
    }

    @Override
    public void add(Context context, AppItem appItem) {
        DatabaseWrapper databaseWrapper = new DatabaseWrapper(context);
        SQLiteDatabase database = databaseWrapper.getReadableDatabase();

        String query = "INSERT OR REPLACE INTO " + TABLE_NAME + "(" + COLUMN_NAME + ", " + COLUMN_VALUE + ") VALUES ( '" + appItem.get_name() + "', '" + appItem.get_value() + "' )";
        database.execSQL(query);
        database.close();
    }

    public void add(Context context, String name, String value){
        add(context, new AppItem(name, value));
    }

    public String get(Context context, String name){
        DatabaseWrapper databaseWrapper = new DatabaseWrapper(context);
        SQLiteDatabase database = databaseWrapper.getReadableDatabase();
        Cursor cursor =  database.rawQuery("SELECT * FROM "+TABLE_NAME+" where "+COLUMN_NAME+" =?", new String[]{name});
        //Cursor cursor = database.rawQuery("SELECT * FROM app_items where name ='seller_token'", null);
        try{
            return cursorToObject(cursor).get_value();
        } catch (Exception ex){
            ex.printStackTrace();
            return null;
        }
    }

    @Override
    public void clearAll(Context context) {
        DatabaseWrapper databaseWrapper = new DatabaseWrapper(context);
        SQLiteDatabase database = databaseWrapper.getReadableDatabase();
        database.delete(TABLE_NAME, null, null);
    }

    @Override
    public List<AppItem> getAll(Context context) {
        DatabaseWrapper databaseWrapper = new DatabaseWrapper(context);
        SQLiteDatabase database = databaseWrapper.getReadableDatabase();
        List<AppItem> historyList = new ArrayList<>();

        Cursor cursor = database.rawQuery("SELECT * FROM " + TABLE_NAME, null);
        try {
            if (cursor.moveToFirst()) {
                do {
                    AppItem h = cursorToObject(cursor);
                    historyList.add(h);
                } while(cursor.moveToNext());
            }
        } catch (Exception e) {
            Log.d(TAG, "Error while trying to get history from database");
        } finally {
            if (cursor != null && !cursor.isClosed()) {
                cursor.close();
            }
        }
        database.close();

        return historyList;
    }

}
