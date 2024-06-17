package org.acme;

import io.smallrye.mutiny.Multi;
import io.vertx.core.json.JsonObject;
import io.vertx.mutiny.pgclient.PgPool;
import io.vertx.mutiny.sqlclient.Row;

public class Student {
    private Long id;
    private String firstName;
    private String lastName;
    private String emailAddress;
    private String phone;

    public Student() {
    }

    public Student(Long id, String firstName, String lastName, String emailAddress, String phone) {
        this.id = id;
        this.firstName = firstName;
        this.lastName = lastName;
        this.emailAddress = emailAddress;
        this.phone = phone;
    }

    public static Multi<Student> findAll(PgPool client) {
        return client.query("SELECT id, first_name, last_name, email_address, phone FROM student").execute()
                .onItem().transformToMulti(set -> Multi.createFrom().iterable(set))
                .onItem().transform(Student::from);
    }

    private static Student from(Row row) {
        return new Student(row.getLong("id"),
                row.getString("first_name"),
                row.getString("last_name"),
                row.getString("email_address"),
                row.getString("phone")
        );
    }

    public Long getId() {
        return id;
    }

    public void setId(Long id) {
        this.id = id;
    }

    public String getFirstName() {
        return firstName;
    }

    public void setFirstName(String firstName) {
        this.firstName = firstName;
    }

    public String getLastName() {
        return lastName;
    }

    public void setLastName(String lastName) {
        this.lastName = lastName;
    }

    public String getEmailAddress() {
        return emailAddress;
    }

    public void setEmailAddress(String emailAddress) {
        this.emailAddress = emailAddress;
    }

    public String getPhone() {
        return phone;
    }

    public void setPhone(String phone) {
        this.phone = phone;
    }

    public JsonObject toJson() {
        return JsonObject.mapFrom(this);
    }
}
