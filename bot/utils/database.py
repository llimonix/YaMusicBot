import aiosqlite


class DataBase:
    @staticmethod
    async def create_table():
        async with aiosqlite.connect("servers.db") as conn:
            await conn.execute('''
                CREATE TABLE IF NOT EXISTS servers (
                    id INTEGER PRIMARY KEY,
                    premium INTEGER DEFAULT 0,
                    info INTEGER DEFAULT 0,
                    role INTEGER DEFAULT 0
                )
            ''')
            await conn.commit()

    @staticmethod
    async def server_exists(server_id):
        async with aiosqlite.connect("servers.db") as conn:
            cursor = await conn.execute(
                "SELECT * FROM servers WHERE id = ?",
                (server_id,)
            )
            return await cursor.fetchone()

    @staticmethod
    async def insert_server(server_id, channel_id):
        async with aiosqlite.connect("servers.db") as conn:
            await conn.execute(
                "INSERT INTO servers (id, info) VALUES (?, ?)",
                (server_id, channel_id)
            )
            await conn.commit()

    @staticmethod
    async def insert_role(server_id, role_id):
        async with aiosqlite.connect("servers.db") as conn:
            await conn.execute(
                "INSERT INTO servers (id, role) VALUES (?, ?)",
                (server_id, role_id)
            )
            await conn.commit()

    @staticmethod
    async def update_role(server_id, role_id):
        async with aiosqlite.connect("servers.db") as conn:
            await conn.execute(
                "UPDATE servers SET role = ? WHERE id = ?",
                (role_id, server_id)
            )
            await conn.commit()

    @staticmethod
    async def insert_info(server_id, info_id):
        async with aiosqlite.connect("servers.db") as conn:
            await conn.execute(
                "INSERT INTO servers (id, info) VALUES (?, ?)",
                (server_id, info_id)
            )
            await conn.commit()

    @staticmethod
    async def update_info(server_id, info_id):
        async with aiosqlite.connect("servers.db") as conn:
            await conn.execute(
                "UPDATE servers SET info = ? WHERE id = ?",
                (info_id, server_id)
            )
            await conn.commit()

    @staticmethod
    async def select_role(server_id):
        async with aiosqlite.connect("servers.db") as conn:
            async with conn.execute("SELECT role FROM servers WHERE id = ?",
                                    (server_id,)) as cursor:
                role = await cursor.fetchone()

                if role is None:
                    return role

                return role[0]

    @staticmethod
    async def select_guilds_info():
        async with aiosqlite.connect("servers.db") as conn:
            async with conn.execute("SELECT info, id FROM servers WHERE info != 0") as cursor:
                guilds = await cursor.fetchall()
                return guilds


db = DataBase()
