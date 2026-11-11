package uz.ustago.app

import org.junit.Assert.*
import org.junit.Test
import uz.ustago.app.util.*

class UtilsTest {
    @Test fun moneyUsesWholeSomAndSpaces() {
        assertEquals("80 000 so'm", formatSom(80000))
        assertEquals("1 250 000 so'm", formatSom(1250000))
    }
    @Test fun emailIsTrimmedAndCaseNormalised() {
        assertEquals("airen@example.com", normalEmail("  Airen@Example.COM  "))
    }
    @Test fun emailRequiresDomain() {
        assertTrue(validEmail("airen@example.com"))
        assertFalse(validEmail("airen@"))
        assertFalse(validEmail("airen example.com"))
    }
    @Test fun passwordLengthHasBounds() {
        assertFalse(validPassword("short"))
        assertTrue(validPassword("GoodPass123"))
        assertFalse(validPassword("x".repeat(129)))
    }
    @Test fun plateRejectsBlankAndPunctuation() {
        assertTrue(validPlate("01 A 123 BC"))
        assertFalse(validPlate("   "))
        assertFalse(validPlate("01@123"))
    }
    @Test fun saltedPasswordsVerifyAndRejectWrongPassword() {
        val first = Passwords.hash("GoodPass123")
        val second = Passwords.hash("GoodPass123")
        assertNotEquals(first, second)
        assertTrue(Passwords.verify("GoodPass123", first))
        assertFalse(Passwords.verify("WrongPass", first))
        assertFalse(Passwords.verify("GoodPass123", "broken"))
    }
}
