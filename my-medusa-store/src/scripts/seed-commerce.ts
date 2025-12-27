import { ExecArgs } from "@medusajs/framework/types";
import { Modules } from "@medusajs/framework/utils";
import { createProductCategoriesWorkflow } from "@medusajs/medusa/core-flows";

export default async function seedCommerce({ container }: ExecArgs) {
  const productModuleService = container.resolve(Modules.PRODUCT);
  const logger = container.resolve("logger");

  logger.info("Seeding Commerce specific categories...");

  const ensureCategory = async (name, handle) => {
    try {
        const existing = await productModuleService.listProductCategories({ handle: [handle] });
        if (existing.length > 0) return existing[0];

        const { result } = await createProductCategoriesWorkflow(container).run({
            input: {
              product_categories: [{
                name,
                handle,
                is_active: true,
              }],
            },
        });
        return result[0];
    } catch (e) {
        const existing = await productModuleService.listProductCategories({ handle: [handle] });
        if (existing.length > 0) return existing[0];
        logger.error(`Failed to create or find category ${handle}: ${e.message}`);
        return null;
    }
  };

  const featuredCat = await ensureCategory("Homepage Featured", "hidden-homepage-featured-items");
  const carouselCat = await ensureCategory("Homepage Carousel", "hidden-homepage-carousel");

  if (!featuredCat && !carouselCat) {
      logger.error("Could not ensure categories exist. Exiting.");
      return;
  }

  const products = await productModuleService.listProducts({}, { take: 10, relations: ["categories"] });

  if (products.length === 0) {
    logger.warn("No products found to seed into commerce categories.");
    return;
  }

  logger.info(`Found ${products.length} products. Assigning to categories...`);

  const addCategoryToProduct = async (product, categoryId) => {
    const currentCatIds = product.categories?.map(c => c.id) || [];
    if (!currentCatIds.includes(categoryId)) {
        await productModuleService.updateProducts(product.id, {
            category_ids: [...currentCatIds, categoryId]
        });
        logger.info(`Added product ${product.handle} to category ${categoryId}`);
    }
  };

  if (featuredCat) {
      for (const product of products.slice(0, 3)) {
        const p = await productModuleService.retrieveProduct(product.id, { relations: ["categories"] });
        await addCategoryToProduct(p, featuredCat.id);
      }
  }

  if (carouselCat) {
      for (const product of products) {
        const p = await productModuleService.retrieveProduct(product.id, { relations: ["categories"] });
        await addCategoryToProduct(p, carouselCat.id);
      }
  }

  logger.info("Commerce seeding finished.");
}
