package org.acme;

import io.smallrye.mutiny.Multi;
import io.vertx.mutiny.pgclient.PgPool;
import jakarta.inject.Inject;
import jakarta.ws.rs.GET;
import jakarta.ws.rs.Path;
import org.jboss.logging.Logger;

@Path("/student")
public class StudentResource {

    // @Inject
    private final PgPool client;

    private static final Logger LOG = Logger.getLogger(StudentResource.class);


    public StudentResource (PgPool client) {
        this.client = client;
    }

    @GET
    @Path("/all")
    public Multi<Student> get() {
        return Student.findAll(client)
        .onFailure().invoke(err -> LOG.error("Failed to fetch students", err));
    }


}
