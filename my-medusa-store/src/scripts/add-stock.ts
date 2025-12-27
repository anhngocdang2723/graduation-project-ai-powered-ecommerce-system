import { ExecArgs } from "@medusajs/framework/types"
import { ContainerRegistrationKeys, Modules } from "@medusajs/framework/utils"

/**
 * Script to UPDATE stock quantities for all products in Medusa
 * Usage: docker exec -it medusa_backend npx medusa exec ./src/scripts/add-stock.ts
 */

export default async function addStockToProducts({ container }: ExecArgs) {
  const logger = container.resolve(ContainerRegistrationKeys.LOGGER)
  const query = container.resolve(ContainerRegistrationKeys.QUERY)

  logger.info("Starting stock update process...")

  try {
    // Get all products with variants AND inventory_items
    const { data: products } = await query.graph({
      entity: "product",
      fields: [
        "id",
        "title",
        "variants.*",
        "variants.id",
        "variants.title",
        "variants.sku",
        "variants.inventory_items.*",
        "variants.inventory_items.inventory_item_id",
      ],
    })

    logger.info(`Found ${products.length} products`)

    // Get inventory and stock location services
    const inventoryService = container.resolve(Modules.INVENTORY)
    const stockLocationService = container.resolve(Modules.STOCK_LOCATION)

    // Get default stock location
    const stockLocations = await stockLocationService.listStockLocations({})
    
    if (stockLocations.length === 0) {
      logger.error("No stock location found. Please create one in the Medusa admin first.")
      throw new Error("No stock location available")
    }

    const defaultLocation = stockLocations[0]
    logger.info(`Using stock location: ${defaultLocation.id} - ${defaultLocation.name}`)

    const defaultStockQuantity = 100 // Default quantity to add
    let processedVariants = 0
    let updated = 0
    let created = 0

    // Process each product and variant
    for (const product of products) {
      if (!product.variants || product.variants.length === 0) {
        logger.warn(`Product ${product.title} has no variants, skipping...`)
        continue
      }

      logger.info(`Processing product: ${product.title} (${product.variants.length} variants)`)

      for (const variant of product.variants) {
        try {
          processedVariants++

          // Each variant should have an inventory_items link
          if (!variant.inventory_items || variant.inventory_items.length === 0) {
            logger.warn(`  No inventory item linked for ${variant.title || variant.sku}, skipping...`)
            continue
          }

          const inventoryItemId = variant.inventory_items[0].inventory_item_id

          // Check if inventory level exists
          const [existingLevel] = await inventoryService.listInventoryLevels({
            inventory_item_id: inventoryItemId,
            location_id: defaultLocation.id,
          })

          if (existingLevel) {
            // Update existing level
            await inventoryService.updateInventoryLevels([{
              id: existingLevel.id,
              inventory_item_id: inventoryItemId,
              location_id: defaultLocation.id,
              stocked_quantity: defaultStockQuantity,
            }])
            updated++
            logger.info(`  ✓ Updated ${variant.title || variant.sku} to ${defaultStockQuantity} units`)
          } else {
            // Create new level
            await inventoryService.createInventoryLevels([{
              inventory_item_id: inventoryItemId,
              location_id: defaultLocation.id,
              stocked_quantity: defaultStockQuantity,
            }])
            created++
            logger.info(`  ✓ Created stock for ${variant.title || variant.sku}: ${defaultStockQuantity} units`)
          }

        } catch (error) {
          logger.error(`  Error processing variant ${variant.id}: ${error.message}`)
        }
      }
    }

    logger.info("\n" + "=".repeat(60))
    logger.info("Stock update completed!")
    logger.info("=".repeat(60))
    logger.info(`Total products processed: ${products.length}`)
    logger.info(`Total variants processed: ${processedVariants}`)
    logger.info(`Inventory levels created: ${created}`)
    logger.info(`Inventory levels updated: ${updated}`)
    logger.info("=".repeat(60))

  } catch (error) {
    logger.error("Error adding stock to products:", error)
    throw error
  }
}
