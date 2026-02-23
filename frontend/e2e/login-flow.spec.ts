import { test, expect } from '@playwright/test'

test.describe('Login flow', () => {
  test('user can log in and see the dashboard', async ({ page }) => {
    // Given I navigate to the app
    await page.goto('/')

    // I see the login page
    await expect(page.locator('.login-container')).toBeVisible()
    await expect(page.locator('h1')).toContainText('Login to Fab UI')

    // When I enter credentials and click Login
    await page.fill('#username', 'admin')
    await page.fill('#password', 'admin')
    await page.click('.login-btn')

    // Then I see the dashboard
    await expect(page.locator('.dashboard h1')).toContainText('QCI Foundry Services')

    // And the dock navigation is visible with Foundry active
    await expect(page.locator('.dock-wrapper')).toBeVisible()
    await expect(page.locator('.dock-item.active').first()).toBeVisible()
  })
})
