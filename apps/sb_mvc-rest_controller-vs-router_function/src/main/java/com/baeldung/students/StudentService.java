package com.baeldung.students;

import java.util.ArrayList;
import java.util.Arrays;
import java.util.List;
import java.util.Map;
import java.util.concurrent.CompletableFuture;
import java.util.concurrent.atomic.AtomicLong;
import java.util.function.Function;
import java.util.stream.Collectors;

import org.springframework.stereotype.Service;

@Service
public class StudentService {
    
    // DB repository mock
    private Map<Long, Student> repository = Arrays.stream(
        new Student[]{
                new Student(1, "Alan","Turing"),
                new Student(2, "Sebastian","Bach"),
                new Student(3, "Pablo","Picasso"),
        })
        .collect(Collectors.toConcurrentMap(Student::getId, Function.identity()));

    public CompletableFuture<List<Student>> readAll() {
        return CompletableFuture.supplyAsync(() -> new ArrayList<>(repository.values()));
    }
}
