package com.example.VertX_PG_client;

import io.vertx.core.AbstractVerticle;
import io.vertx.core.Vertx;
import io.vertx.core.json.JsonArray;
import io.vertx.core.json.JsonObject;
import io.vertx.ext.web.Router;
import io.vertx.ext.web.RoutingContext;
import io.vertx.ext.web.handler.BodyHandler;
import io.vertx.pgclient.PgConnectOptions;
import io.vertx.pgclient.PgPool;
import io.vertx.sqlclient.PoolOptions;
import io.vertx.sqlclient.Row;
import io.vertx.sqlclient.SqlConnection;

public class MainVerticle extends AbstractVerticle {

  private PgPool client;

  public static void main(String[] args) {
    Vertx vertx = Vertx.vertx();
    vertx.deployVerticle(new MainVerticle());
  }

  @Override
  public void start() {
    PgConnectOptions connectOptions = new PgConnectOptions()
      .setPort(5432)
      .setHost("localhost")
      .setDatabase("my_database")
      .setUser("my_username")
      .setPassword("my_password");

    PoolOptions poolOptions = new PoolOptions().setMaxSize(100);

    client = PgPool.pool(vertx, connectOptions, poolOptions);

    Router router = Router.router(vertx);
    router.route().handler(BodyHandler.create());
    router.get("/student/all").handler(this::getStudents);

    vertx.createHttpServer().requestHandler(router).listen(8080, http -> {
      if (http.succeeded()) {
        System.out.println("HTTP server started on port 8080");
      } else {
        System.out.println("HTTP server failed to start");
      }
    });
  }

  private void getStudents(RoutingContext routingContext) {
    client.getConnection(ar -> {
      if (ar.succeeded()) {
        SqlConnection connection = ar.result();
        connection.query("SELECT * FROM student").execute(res -> {
          if (res.succeeded()) {
            JsonArray jsonArray = new JsonArray();
            for (Row row : res.result()) {
              JsonObject jsonObject = new JsonObject()
                .put("id", row.getInteger("id"))
                .put("firstName", row.getString("first_name"))
                .put("lastName", row.getString("last_name"))
                .put("emailAddress", row.getString("email_address"))
                .put("phone", row.getString("phone"));
              jsonArray.add(jsonObject);
            }
            routingContext.response()
              .putHeader("content-type", "application/json")
              .end(jsonArray.encode());
          } else {
            routingContext.response().setStatusCode(500).end(res.cause().toString());
          }
          connection.close();
        });
      } else {
        routingContext.response().setStatusCode(500).end(ar.cause().toString());
      }
    });
  }
}

