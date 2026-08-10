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

class BcimsLoginOnlyProdSimulation extends Simulation {

  private val loginBasicAuth = sys.env.getOrElse("BCI_PRUEBAS_CARGA_BASIC_TOKEN", "")

  // Función para enmascarar tokens e información sensible
  private def maskValue(value: String, visibleChars: Int = 3): String = {
    if (value == null || value.isEmpty) {
      "[VACÍO]"
    } else if (value.length <= visibleChars * 2) {
      "***"
    } else {
      val prefix = value.take(visibleChars)
      val suffix = value.takeRight(visibleChars)
      s"$prefix****$suffix"
    }
  }

  before {
    println("===================================================")
    println("[LOGIN ONLY PROD] Iniciando prueba de Login")
    // Ejemplo de salida: G74****YerqO
    println(s"[CONFIG] Basic Auth Token cargado: ${maskValue(loginBasicAuth)}") 
    println("===================================================")
  }

  // Resto de la simulación...
  private val httpProtocol = http
    .baseUrl("https://apibackprod.bci.cl")
    .disableWarmUp

  private val loginScenario = scenario("Solo Login Prod")
    .exec { session =>
      // También puedes enmascarar variables dinámicas guardadas en la sesión
      val tracking = session("trackingId").asOption[String].getOrElse("")
      println(s"[EXEC] Processing Tracking-Id: ${maskValue(tracking, 4)}")
      session
    }

  setUp(loginScenario.inject(atOnceUsers(1))).protocols(httpProtocol)
}
```


#### Short summary: 

empty definition using pc, found symbol in pc: 