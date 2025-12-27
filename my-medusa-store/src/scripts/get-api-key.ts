import { ExecArgs } from "@medusajs/framework/types";
import { Modules } from "@medusajs/framework/utils";

export default async function getApiKey({ container }: ExecArgs) {
  const apiKeyModule = container.resolve(Modules.API_KEY);
  
  const apiKeys = await apiKeyModule.listApiKeys({
    title: "Webshop",
    type: "publishable",
  });

  if (apiKeys.length > 0) {
    console.log("MEDUSA_API_KEY=" + apiKeys[0].token);
  } else {
    console.log("No Publishable API Key found with title 'Webshop'");
  }
}
