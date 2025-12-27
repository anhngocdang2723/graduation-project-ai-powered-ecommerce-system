import { ExecArgs } from "@medusajs/framework/types"
import { ContainerRegistrationKeys, Modules } from "@medusajs/framework/utils"

/**
 * Advanced script to add stock with custom quantities per product
 * Usage: docker exec -it medusa_backend npx medusa exec ./src/scripts/add-stock-custom.ts
 * 
 * Configure stock quantities below before running
 */

// Configuration: Set stock quantities per product SKU or for all products
const STOCK_CONFIG = {
  // Default stock for all products if not specified
  defaultQuantity: 100,
  
  // Custom quantities for specific SKUs
  customQuantities: {
    // "PRODUCT-SKU-001": 500,
    // "BACKPACK-001": 250,
    // Add your custom SKUs here
  } as Record<string, number>,
  
  // Set stock based on price ranges
  priceRanges: {
    enabled: false,
    ranges: [
      { minPrice: 0, maxPrice: 50, quantity: 200 },      // Cheap items: high stock
      { minPrice: 50, maxPrice: 200, quantity: 100 },    // Medium: normal stock
      { minPrice: 200, maxPrice: 999999, quantity: 50 }, // Expensive: low stock
    ]
  }
}

export default async function addStockWithCustomQuantities({ container }: ExecArgs) {
  const logger = container.resolve(ContainerRegistrationKeys.LOGGER)
  const query = container.resolve(ContainerRegistrationKeys.QUERY)
  const remoteLink = container.resolve(ContainerRegistrationKeys.REMOTE_LINK)

  logger.info("Starting custom stock addition process...")
  logger.info(`Default quantity: ${STOCK_CONFIG.defaultQuantity}`)

  try {
    const { data: products } = await query.graph({
      entity: "product",
      fields: [
        "id",
        "title",
        "variants.*",
        "variants.id",
        "variants.title",
        "variants.sku",
        "variants.prices.*",
      ],
    })

    const inventoryModuleService = container.resolve(Modules.INVENTORY)
    const stockLocationService = container.resolve(Modules.STOCK_LOCATION)

    const stockLocations = await stockLocationService.listStockLocations({})
    const defaultLocation = stockLocations[0]

    if (!defaultLocation) {
      throw new Error("No stock location found. Please create one first.")
    }

    logger.info(`Using location: ${defaultLocation.name}`)

    const stats = {
      processed: 0,
      created: 0,
      updated: 0,
      skipped: 0,
    }

    for (const product of products) {
      for (const variant of product.variants || []) {
        try {
          const sku = variant.sku || `VAR-${variant.id}`
          
          // Determine stock quantity
          let stockQuantity = STOCK_CONFIG.defaultQuantity

          // Check custom SKU quantities first
          if (STOCK_CONFIG.customQuantities[sku]) {
            stockQuantity = STOCK_CONFIG.customQuantities[sku]
            logger.info(`  Using custom quantity for ${sku}: ${stockQuantity}`)
          }
          // Check price-based quantities
          else if (STOCK_CONFIG.priceRanges.enabled && variant.prices?.length > 0) {
            const price = variant.prices[0]?.amount || 0
            const priceInDollars = price / 100 // Convert cents to dollars
            
            for (const range of STOCK_CONFIG.priceRanges.ranges) {
              if (priceInDollars >= range.minPrice && priceInDollars < range.maxPrice) {
                stockQuantity = range.quantity
                logger.info(`  Price-based quantity for ${sku} ($${priceInDollars}): ${stockQuantity}`)
                break
              }
            }
          }

          // Get or create inventory item
          let inventoryItems = await inventoryModuleService.listInventoryItems({ sku })
          let inventoryItem

          if (inventoryItems.length === 0) {
            const createdItems = await inventoryModuleService.createInventoryItems([{
              sku,
              title: variant.title || product.title,
            }])
            inventoryItem = createdItems[0]
            stats.created++
          } else {
            inventoryItem = inventoryItems[0]
          }

          // Link variant to inventory
          try {
            await remoteLink.create({
              productService: { variant_id: variant.id },
              inventoryService: { inventory_item_id: inventoryItem.id },
            })
          } catch (e) {
            // Link exists
          }

          // Create or update inventory level
          const levels = await inventoryModuleService.listInventoryLevels({
            inventory_item_id: inventoryItem.id,
            location_id: defaultLocation.id,
          })

          if (levels.length > 0) {
            await inventoryModuleService.updateInventoryLevels([
              {
                id: levels[0].id,
                stocked_quantity: stockQuantity,
                inventory_item_id: inventoryItem.id,
                location_id: defaultLocation.id
              }
            ])
            stats.updated++
          } else {
            await inventoryModuleService.createInventoryLevels([{
              inventory_item_id: inventoryItem.id,
              location_id: defaultLocation.id,
              stocked_quantity: stockQuantity,
            }])
            stats.created++
          }

          stats.processed++
          logger.info(`  ✓ ${product.title} - ${variant.title || sku}: ${stockQuantity} units`)

        } catch (error) {
          stats.skipped++
          logger.error(`  ✗ Error: ${error.message}`)
        }
      }
    }

    logger.info("\n" + "=".repeat(60))
    logger.info("📦 Stock Addition Summary")
    logger.info("=".repeat(60))
    logger.info(`Variants processed: ${stats.processed}`)
    logger.info(`Items created: ${stats.created}`)
    logger.info(`Items updated: ${stats.updated}`)
    logger.info(`Skipped: ${stats.skipped}`)
    logger.info("=".repeat(60))

  } catch (error) {
    logger.error("Fatal error:", error)
    throw error
  }
}
