import requests
from typing import Dict, Optional
from app.core.config import settings


class QuickBooksService:
    """QuickBooks Integration Service"""

    def __init__(self):
        self.client_id = settings.QUICKBOOKS_CLIENT_ID
        self.client_secret = settings.QUICKBOOKS_CLIENT_SECRET
        self.redirect_uri = settings.QUICKBOOKS_REDIRECT_URI
        self.base_url = "https://quickbooks.api.intuit.com/v3"
        self.auth_url = "https://appcenter.intuit.com/connect/oauth2"

    def get_authorization_url(self) -> str:
        """Get QuickBooks OAuth authorization URL"""
        params = {
            "client_id": self.client_id,
            "redirect_uri": self.redirect_uri,
            "response_type": "code",
            "scope": "com.intuit.quickbooks.accounting",
            "state": "security_token"  # Should be random in production
        }
        query_string = "&".join(f"{k}={v}" for k, v in params.items())
        return f"{self.auth_url}?{query_string}"

    def exchange_code_for_tokens(self, code: str) -> Dict:
        """Exchange authorization code for access tokens"""
        if not self.client_id or not self.client_secret:
            return {"error": "QuickBooks credentials not configured"}

        token_url = "https://oauth.platform.intuit.com/oauth2/v1/tokens/bearer"
        data = {
            "grant_type": "authorization_code",
            "code": code,
            "redirect_uri": self.redirect_uri
        }

        try:
            response = requests.post(
                token_url,
                data=data,
                auth=(self.client_id, self.client_secret),
                headers={"Accept": "application/json"}
            )
            return response.json()
        except Exception as e:
            return {"error": str(e)}

    def sync_invoice(self, invoice_data: Dict, access_token: str, realm_id: str) -> Dict:
        """
        Sync invoice to QuickBooks
        
        Args:
            invoice_data: Invoice data to sync
            access_token: QuickBooks access token
            realm_id: QuickBooks company ID
        """
        if not access_token:
            return {"status": "skipped", "message": "No QuickBooks access token"}

        # Transform invoice data to QuickBooks format
        qb_invoice = self._transform_to_quickbooks_format(invoice_data)

        try:
            url = f"{self.base_url}/company/{realm_id}/invoice"
            headers = {
                "Authorization": f"Bearer {access_token}",
                "Accept": "application/json",
                "Content-Type": "application/json"
            }

            response = requests.post(url, json=qb_invoice, headers=headers)

            if response.status_code == 200:
                return {
                    "status": "success",
                    "quickbooks_id": response.json().get("Invoice", {}).get("Id"),
                    "message": "Invoice synced to QuickBooks"
                }
            else:
                return {
                    "status": "error",
                    "message": f"QuickBooks sync failed: {response.text}"
                }

        except Exception as e:
            return {"status": "error", "message": str(e)}

    def _transform_to_quickbooks_format(self, invoice_data: Dict) -> Dict:
        """Transform internal invoice format to QuickBooks format"""
        qb_invoice = {
            "DocNumber": invoice_data.get("invoice_number"),
            "TxnDate": invoice_data.get("invoice_date"),
            "DueDate": invoice_data.get("due_date"),
            "Line": []
        }

        # Add line items
        for idx, item in enumerate(invoice_data.get("line_items", []), 1):
            qb_invoice["Line"].append({
                "Id": str(idx),
                "LineNum": idx,
                "Amount": item.get("amount", 0),
                "DetailType": "SalesItemLineDetail",
                "SalesItemLineDetail": {
                    "Qty": item.get("quantity", 1),
                    "UnitPrice": item.get("unit_price", 0),
                    "ItemRef": {
                        "name": item.get("description", "")
                    }
                }
            })

        # Add customer reference if available
        if invoice_data.get("customer_name"):
            qb_invoice["CustomerRef"] = {
                "name": invoice_data["customer_name"]
            }

        return qb_invoice


# Singleton instance
quickbooks_service = QuickBooksService()
