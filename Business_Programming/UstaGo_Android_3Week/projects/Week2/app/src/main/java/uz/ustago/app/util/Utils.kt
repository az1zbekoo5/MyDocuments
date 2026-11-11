package uz.ustago.app.util

import java.security.MessageDigest
import java.security.SecureRandom
import java.text.SimpleDateFormat
import java.util.Date
import java.util.Locale
import javax.crypto.SecretKeyFactory
import javax.crypto.spec.PBEKeySpec

fun formatSom(amount: Long): String = String.format(Locale.US, "%,d", amount).replace(',', ' ') + " so'm"
fun formatTime(value: Long): String = SimpleDateFormat("EEE, dd MMM yyyy · HH:mm", Locale.ENGLISH).format(Date(value))
fun normalEmail(value: String): String = value.trim().lowercase(Locale.ROOT)
fun validEmail(value: String): Boolean = Regex("^[A-Za-z0-9.!#%&'*+/=?^_`{|}~-]+@[A-Za-z0-9-]+(?:\\.[A-Za-z0-9-]+)+$").matches(value)
fun validPassword(value: String): Boolean = value.length in 8..128
fun validPlate(value: String): Boolean = value.trim().length in 5..15 &&
    value.trim().all { it.isLetterOrDigit() || it == ' ' || it == '-' }

// PBKDF2-HMAC-SHA1 is available on API 24. A random salt prevents identical hashes.
// This is device-local coursework authentication; a real service needs server auth.
object Passwords {
    private const val iterations = 210000
    private fun hex(bytes: ByteArray) = bytes.joinToString("") { "%02x".format(it.toInt() and 255) }
    private fun unhex(text: String): ByteArray = text.chunked(2).map { it.toInt(16).toByte() }.toByteArray()
    private fun derive(password: String, salt: ByteArray, rounds: Int): ByteArray {
        val spec = PBEKeySpec(password.toCharArray(), salt, rounds, 256)
        return try { SecretKeyFactory.getInstance("PBKDF2WithHmacSHA1").generateSecret(spec).encoded }
        finally { spec.clearPassword() }
    }
    fun hash(password: String): String {
        val salt = ByteArray(16).also { SecureRandom().nextBytes(it) }
        return "$iterations:${hex(salt)}:${hex(derive(password, salt, iterations))}"
    }
    fun verify(password: String, encoded: String): Boolean = try {
        val parts = encoded.split(':')
        val rounds = parts[0].toInt()
        if (parts.size != 3 || rounds != iterations || parts[1].length != 32 || parts[2].length != 64) false
        else MessageDigest.isEqual(unhex(parts[2]), derive(password, unhex(parts[1]), rounds))
    } catch (_: Exception) { false }
}
