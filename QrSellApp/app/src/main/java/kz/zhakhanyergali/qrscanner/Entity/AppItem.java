package kz.zhakhanyergali.qrscanner.Entity;

public class AppItem {
    private String name;
    private String value;

    public AppItem(String name, String value){
        this.name = name;
        this.value = value;
    }
    public String get_name(){
        return this.name;
    }
    public String get_value(){
        return this.value;
    }
}
