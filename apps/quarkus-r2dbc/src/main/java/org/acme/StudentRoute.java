package org.acme;

import io.smallrye.mutiny.Multi;
import io.vertx.core.http.HttpServerResponse;
import io.vertx.mutiny.pgclient.PgPool;
import jakarta.enterprise.context.ApplicationScoped;

import jakarta.enterprise.event.Observes;
import org.jboss.logging.Logger;
import jakarta.inject.Inject;
import io.vertx.ext.web.Router;
import io.vertx.ext.web.RoutingContext;
import io.vertx.mutiny.sqlclient.Row;

@ApplicationScoped
public class StudentRoute {

    private static final Logger LOG = Logger.getLogger(StudentRoute.class);

    @Inject
    PgPool client;

    public void init(@Observes Router router) {
        router.get("/student/all").handler(this::getAllStudents);
    }

    private void getAllStudents(RoutingContext rc) {
        HttpServerResponse response = rc.response();
        response.setChunked(true);  // Enable chunked transfer encoding

        client.query("SELECT id, first_name, last_name, email_address, phone FROM student")
                .execute()
                .onItem().transformToMulti(set -> Multi.createFrom().iterable(set))
                .onItem().transform(this::from)
                .subscribe().with(
                        student -> response.write(student.toJson().encode() + "\n"),  // Convert the student object to JSON string
                        failure -> {
                            LOG.error("Failed to fetch students", failure);
                            response.setStatusCode(500).end("Internal Server Error");
                        },
                        response::end
                );
    }

    private Student from(Row row) {
        return new Student(row.getLong("id"),
                row.getString("first_name"),
                row.getString("last_name"),
                row.getString("email_address"),
                row.getString("phone"));
    }
}
