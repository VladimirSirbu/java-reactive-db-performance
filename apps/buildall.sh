export JAVA_HOME=/usr/lib/jvm/java-11-openjdk-amd64

cd WEB_MVC_JDBC
JAVA_HOME=$JAVA_HOME mvn clean package
mv target/*.jar ..
cd ..

cd WEB_FLUX_JDBC
JAVA_HOME=$JAVA_HOME mvn clean package
mv target/*.jar ..
cd ..

cd WEB_MVC_R2DBC
JAVA_HOME=$JAVA_HOME mvn clean package
mv target/*.jar ..
cd ..

cd WEB_FLUX_R2DBC
JAVA_HOME=$JAVA_HOME mvn clean package
mv target/*.jar ..
cd ..

cd quarkus-r2dbc
JAVA_HOME=$JAVA_HOME mvn clean package
mv target/*.jar ..
cd ..

cd VertX_PG_client
JAVA_HOME=$JAVA_HOME mvn clean package
mv target/*fat.jar ..
cd ..