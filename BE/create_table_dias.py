
import pyodbc
from app.database import get_connection1

def create_table():
    conn = get_connection1()
    cursor = conn.cursor()
    
    try:
        # Check if table exists
        cursor.execute("""
            IF NOT EXISTS (SELECT * FROM sys.objects WHERE object_id = OBJECT_ID(N'[dbo].[CampanaConfiguracionDias]') AND type in (N'U'))
            BEGIN
                CREATE TABLE [dbo].[CampanaConfiguracionDias](
                    [ID] [int] IDENTITY(1,1) NOT NULL,
                    [IDCampana] [int] NOT NULL,
                    [Fecha] [date] NOT NULL,
                    [EsHabil] [bit] NOT NULL,
                    [FechaActualizacion] [datetime] DEFAULT (getdate()),
                    PRIMARY KEY CLUSTERED 
                    (
                        [ID] ASC
                    )WITH (PAD_INDEX = OFF, STATISTICS_NORECOMPUTE = OFF, IGNORE_DUP_KEY = OFF, ALLOW_ROW_LOCKS = ON, ALLOW_PAGE_LOCKS = ON) ON [PRIMARY]
                ) ON [PRIMARY]

                ALTER TABLE [dbo].[CampanaConfiguracionDias]  WITH CHECK ADD  CONSTRAINT [FK_CampanaConfiguracionDias_CampanasQA] FOREIGN KEY([IDCampana])
                REFERENCES [dbo].[CampanasQA] ([IDCampanasQA])

                ALTER TABLE [dbo].[CampanaConfiguracionDias] CHECK CONSTRAINT [FK_CampanaConfiguracionDias_CampanasQA]
                
                PRINT 'Table CampanaConfiguracionDias created successfully.'
            END
            ELSE
            BEGIN
                PRINT 'Table CampanaConfiguracionDias already exists.'
            END
        """)
        conn.commit()
    except Exception as e:
        print(f"Error creating table: {e}")
        conn.rollback()
    finally:
        cursor.close()
        conn.close()

if __name__ == "__main__":
    create_table()
