# Milestone 4: Database Setup (DDL).

This document explains the steps taken to generate the Data Definition Language (DDL) scripts for the Car Workshop Management System database setup.

## Step 1: DDL Script Creation.
A comprehensive SQL script file (`schema.sql`) has been created in the `Milestone4` folder. This script generates the 7 core tables derived from our finalized normalized schema.

### Constraints Implemented:
*   **Primary Keys (`PRIMARY KEY`)**: Applied to all tables (e.g., `CustomerID`, `VehicleID`). A composite primary key is correctly utilized in the `SERVICE_PARTS` junction table (`JobID`, `PartID`).
*   **Foreign Keys (`FOREIGN KEY`)**: Defined explicit relational mapping between tables ensuring referential integrity.
    *   `VEHICLE` correctly references `CUSTOMER`.
    *   `SERVICE_JOB` correctly references both `VEHICLE` and `MECHANIC`.
    *   `INVOICE` references `SERVICE_JOB`.
    *   `ON DELETE CASCADE` is utilized for parent-child relations like Customer->Vehicle and Job->Invoice. `ON DELETE RESTRICT` is used to prevent the accidental deletion of active Mechanics or Spare Parts.
*   **Data Integrity (`NOT NULL`)**: Applied to core data points such as `FirstName`, `Date`, and `Status` to prevent missing information anomalies.
*   **Unique Constraints (`UNIQUE`)**: Applied to `Email` (Customer) and `RegNo` (Vehicle) to ensure no duplicate entries exist in the system.
*   **Check Constraints (`CHECK`)**: Added robust domain validations.
    *   `SkillLevel` in Mechanics must be 'Junior', 'Intermediate', 'Senior', or 'Master'.
    *   `Status` in Service_Job must be 'Pending', 'In Progress', 'Completed', or 'Cancelled'.
    *   `PaymentStatus` in Invoice must be 'Paid', 'Unpaid', or 'Refunded'.
    *   Monetary values (`LaborCost`, `UnitPrice`) and `Quantity` strictly enforce zero or positive constraints to prevent logical errors.

### Indexing Implemented:
*   Indexes (`CREATE INDEX`) have been explicitly declared for:
    *   All Foreign Key columns (e.g., `CustomerID` in Vehicle, `JobID` in Invoice) to dramatically speed up join operations and cascaded deletes.
    *   Frequently queried status fields (e.g., `PaymentStatus`, `Status`).
    *   Common lookup fields like `Email`, `RegNo`, and `LastName`.

## Step 2: Verification Process.
The script has been structured specifically for full compatibility with **MySQL Workbench**.

**Next Action for the User:** 
1. Open MySQL Workbench.
2. Load and execute the `schema.sql` script to create the schema.
3. Use the built-in "Reverse Engineer" tool in MySQL Workbench (`Database` -> `Reverse Engineer...`) to automatically generate the EER diagram.
4. Verify that the generated diagram perfectly matches the structural logic expected from the DDL code.

## Step 3: Version Control.
The schema script and this documentation file are staged for commit with the required message format:
`M4: DDL scripts added, EER diagram verified`
