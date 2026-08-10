file://<WORKSPACE>/Pruebas%20por%20Ambiente/Prod/apibakmstdc/BcimsLoginOnlyProdSimulation.scala
empty definition using pc, found symbol in pc: 
semanticdb not found
empty definition using fallback
non-local guesses:
	 -io/gatling/core/Predef.io.gatling.
	 -io/gatling/http/Predef.io.gatling.
	 -io/gatling.
	 -scala/Predef.io.gatling.
offset: 47
uri: file://<WORKSPACE>/Pruebas%20por%20Ambiente/Prod/apibakmstdc/BcimsLoginOnlyProdSimulation.scala
text:
```scala
package bci.cards.simulation

import io.gatling@@.core.Predef._
import io.gatling.http.Predef._
import java.util.UUID
import java.util.Base64
import java.nio.charset.StandardCharsets

class BcimsLoginOnlyProdSimulation extends Simulation {

  private val baseUrlEnv: String = sys.env.getOrElse("BCI_BASE_URL", "https://apibackprod.bci.cl")
  private val loginEndpoint: String = sys.env.getOrElse(
    "BCI_LOGIN_ENDPOINT",
    "/operaciones/seguridad-y-acceso/ms-loginclientes-util/v1.4/oauth/token"
  )

  // Alineado con el cURL funcional: "app-pruebas-andes" (con 's')
  private val loginApplicationId: String = sys.env.getOrElse("BCI_LOGIN_APPLICATION_ID", "postman")
  private val rawVaultToken: String       = sys.env.getOrElse("BCI_PRUEBAS_CARGA_BASIC_TOKEN", "")

  // Base64 en vivo del par "app-pruebas-andes:token-vault"
  private val loginBasicAuth: String = {
    if (rawVaultToken.nonEmpty) {
      val credentials = s"app-pruebas-andes:$rawVaultToken"
      Base64.getEncoder.encodeToString(credentials.getBytes(StandardCharsets.UTF_8))
    } else {
      ""
    }
  }

  private val usuarios = Vector(Map("rutLogin" -> "15317954-9"))
  private val loginFeeder = usuarios.toArray.circular

  // Función de enmascaramiento para la consola
  private def maskValue(value: String, visibleChars: Int = 3): String = {
    if (value == null || value.isEmpty) "[VACÍO]"
    else if (value.length <= visibleChars * 2) "***"
    else s"${value.take(visibleChars)}****${value.takeRight(visibleChars)}"
  }

  private val httpProtocol = http
    .baseUrl(baseUrlEnv)
    .contentTypeHeader("application/x-www-form-urlencoded")
    .acceptHeader("application/json")
    .disableWarmUp

  private val loginRequest =
    http("POST Login Client Credentials Prod")
      .post(loginEndpoint)
      .header("Authorization", s"Basic $loginBasicAuth": String)
      .header("Accept", "application/json")
      .header("Application-Id", sys.env.getOrElse("BCI_LOGIN_APPLICATION_ID", "postman"): String)
      .header("Channel", sys.env.getOrElse("BCI_LOGIN_CHANNEL", "110"): String)
      .header("Reference-Service", sys.env.getOrElse("BCI_LOGIN_REFERENCE_SERVICE", "postman"): String)
      .header("Reference-Operation", sys.env.getOrElse("BCI_LOGIN_REFERENCE_OPERATION", "login"): String)
      .header("Origin-addr", sys.env.getOrElse("BCI_LOGIN_ORIGIN_ADDR", "7.249.58.150"): String)
      .header("Tracking-Id", "#{trackingId}")
      .formParam("grant_type", "client_credentials")
      .formParam("rut", "#{rutLogin}")
      .check(status.saveAs("responseStatus"))
      .check(status.is(200)) // Gatling marcará KO si el servidor no responde HTTP 200

  private val loginScenario =
    scenario("Solo Login Prod")
      .feed(loginFeeder)
      .exec(session => session.set("trackingId", UUID.randomUUID().toString))
      .exec(loginRequest)
      .exec { session =>
        val tracking = session("trackingId").asOption[String].getOrElse("")
        val status = session("responseStatus").asOption[Int].getOrElse(0)

        println(s"[EXEC] Tracking-Id: ${maskValue(tracking, 4)}")
        println(s"[EXEC] Status HTTP: $status")
        session
      }

  setUp(
    loginScenario.inject(atOnceUsers(1))
  ).protocols(httpProtocol)
    // Fuerza a que Gradle/Pipeline marque FAILED (exit code 1) si hay peticiones KO
    .assertions(
      global.failedRequests.count.is(0),
      details("POST Login Client Credentials Prod").successfulRequests.percent.is(100)
    )

  before {
    println("===================================================")
    println("[LOGIN ONLY PROD] Iniciando prueba de Login")
    println(s"[CONFIG] Basic Auth Base64 inyectado: ${maskValue(loginBasicAuth)}")
    println("===================================================")
  }
}
```


#### Short summary: 

empty definition using pc, found symbol in pc: 