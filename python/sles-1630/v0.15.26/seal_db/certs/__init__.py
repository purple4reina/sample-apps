import os.path

# Path to the RDS certificate
rds_cert_path = os.path.join(os.path.dirname(__file__), "rds-us-east-1-bundle.pem")

__all__ = ["rds_cert_path"]
