package org.example.web_mvc_r2dbc;

import org.springframework.data.annotation.Id;

public class Student {

    @Id
    private Long id;
    private String firstName;
    private String lastName;
    private String emailAddress;
    private String phone;

    public Student() {
    }

    public Student(String firstName, String lastName, String emailAddress, String phone) {
        this.firstName = firstName;
        this.lastName = lastName;
        this.emailAddress = emailAddress;
        this.phone = phone;
    }

    public Long getId() {
        return id;
    }

    public String getFirstName() {
        return firstName;
    }

    public String getLastName() {
        return lastName;
    }

    public String getEmailAddress() {
        return emailAddress;
    }

    public String getPhone() {
        return phone;
    }
}

