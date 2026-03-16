"""
╔══════════════════════════════════════════════════════╗
║         ZONA GENSY — Bot Discord IA                  ║
║         Setup automatique + Assistant Claude         ║
╚══════════════════════════════════════════════════════╝
"""

import discord
from discord.ext import commands
from discord import app_commands
import anthropic
import os
import asyncio

# ─── CONFIGURATION ────────────────────────────────────────────────────────────
DISCORD_TOKEN = os.environ.get("DISCORD_TOKEN")
ANTHROPIC_API_KEY = os.environ.get("ANTHROPIC_API_KEY")

intents = discord.Intents.default()
intents.message_content = True
intents.members = True
intents.guilds = True

bot = commands.Bot(command_prefix="§§§", intents=intents)
ai_client = anthropic.Anthropic(api_key=ANTHROPIC_API_KEY)

# Historique de conversation IA par serveur
ai_histories: dict[int, list] = {}

# ─── STRUCTURE DU SERVEUR ─────────────────────────────────────────────────────
ROLES_CONFIG = [
    {"name": "👑 Fondateur",   "color": discord.Color.from_rgb(231, 76,  60)},
    {"name": "🔧 Admin",       "color": discord.Color.from_rgb(230, 126, 34)},
    {"name": "💼 Équipe",      "color": discord.Color.from_rgb(241, 196, 15)},
    {"name": "🤝 Partenaire",  "color": discord.Color.from_rgb(52,  152, 219)},
    {"name": "📦 Client",      "color": discord.Color.from_rgb(46,  204, 113)},
    {"name": "👀 Nouveau",     "color": discord.Color.from_rgb(149, 165, 166)},
]

SERVER_STRUCTURE = [
    {
        "name": "📌 ACCUEIL",
        "public": True,
        "channels": [
            {"name": "📋-règles-et-charte",        "type": "text"},
            {"name": "🗺️-navigation-du-serveur",   "type": "text"},
            {"name": "📣-annonces",                 "type": "text"},
            {"name": "👋-bienvenue",                "type": "text"},
        ]
    },
    {
        "name": "🏢 QG ZONA GENSY",
        "allowed_roles": ["👑 Fondateur", "🔧 Admin", "💼 Équipe", "🤝 Partenaire"],
        "channels": [
            {"name": "💬-général",              "type": "text"},
            {"name": "🧠-idées-et-stratégie",   "type": "text"},
            {"name": "📅-planning-réunions",    "type": "text"},
            {"name": "🤖-assistant-zona",       "type": "text"},
            {"name": "🎙️-réunion-principale",  "type": "voice"},
            {"name": "🎙️-brainstorming",       "type": "voice"},
        ]
    },
    {
        "name": "📁 RESSOURCES CENTRALES",
        "allowed_roles": ["👑 Fondateur", "🔧 Admin", "💼 Équipe", "🤝 Partenaire"],
        "channels": [
            {"name": "🔗-outils-et-liens",      "type": "text"},
            {"name": "📚-process-et-sops",      "type": "text"},
            {"name": "🎨-assets-et-visuels",    "type": "text"},
            {"name": "📝-templates-messages",   "type": "text"},
            {"name": "🤖-bots-et-automations",  "type": "text"},
        ]
    },
    {
        "name": "🎬 MP4POD",
        "allowed_roles": ["👑 Fondateur", "🔧 Admin", "💼 Équipe"],
        "channels": [
            {"name": "📰-fil-actus",    "type": "text"},
            {"name": "📁-ressources",   "type": "text"},
            {"name": "✅-tâches",       "type": "text"},
        ]
    },
    {
        "name": "⚙️ FLOWAGENT",
        "allowed_roles": ["👑 Fondateur", "🔧 Admin", "💼 Équipe"],
        "channels": [
            {"name": "📰-fil-actus",    "type": "text"},
            {"name": "📁-ressources",   "type": "text"},
            {"name": "✅-tâches",       "type": "text"},
        ]
    },
    {
        "name": "🔮 SCHÉMATICA",
        "allowed_roles": ["👑 Fondateur", "🔧 Admin", "💼 Équipe"],
        "channels": [
            {"name": "📰-fil-actus",    "type": "text"},
            {"name": "📁-ressources",   "type": "text"},
            {"name": "✅-tâches",       "type": "text"},
        ]
    },
    {
        "name": "👗 STYLEAUGENTE",
        "allowed_roles": ["👑 Fondateur", "🔧 Admin", "💼 Équipe"],
        "channels": [
            {"name": "📰-fil-actus",    "type": "text"},
            {"name": "📁-ressources",   "type": "text"},
            {"name": "✅-tâches",       "type": "text"},
        ]
    },
    {
        "name": "🎓 EPA IA",
        "allowed_roles": ["👑 Fondateur", "🔧 Admin", "💼 Équipe"],
        "channels": [
            {"name": "📰-fil-actus",    "type": "text"},
            {"name": "📁-ressources",   "type": "text"},
            {"name": "✅-tâches",       "type": "text"},
        ]
    },
    {
        "name": "🎥 BERLIZE",
        "allowed_roles": ["👑 Fondateur", "🔧 Admin", "💼 Équipe"],
        "channels": [
            {"name": "📰-fil-actus",    "type": "text"},
            {"name": "📁-ressources",   "type": "text"},
            {"name": "✅-tâches",       "type": "text"},
        ]
    },
    {
        "name": "👥 ÉQUIPE",
        "allowed_roles": ["👑 Fondateur", "🔧 Admin", "💼 Équipe"],
        "channels": [
            {"name": "🔒-espace-admins",    "type": "text"},
            {"name": "✅-tâches-du-jour",   "type": "text"},
            {"name": "🚀-onboarding",       "type": "text"},
        ]
    },
    {
        "name": "🤝 CLIENTS",
        "allowed_roles": ["👑 Fondateur", "🔧 Admin", "📦 Client"],
        "channels": [
            {"name": "📩-demandes",         "type": "text"},
            {"name": "📊-suivi-projets",    "type": "text"},
        ]
    },
]

# ─── UI — MENU DE RÔLE ────────────────────────────────────────────────────────
class RoleSelectMenu(discord.ui.Select):
    def __init__(self):
        options = [
            discord.SelectOption(label="💼 Équipe",     description="Membre interne de Zona Gensy",   value="💼 Équipe"),
            discord.SelectOption(label="🤝 Partenaire", description="Collaborateur / partenaire",     value="🤝 Partenaire"),
            discord.SelectOption(label="📦 Client",     description="Client d'une des entités",       value="📦 Client"),
        ]
        super().__init__(
            placeholder="👋 Qui es-tu ? Sélectionne ton rôle...",
            options=options,
            custom_id="zona_role_select"
        )

    async def callback(self, interaction: discord.Interaction):
        guild = interaction.guild
        role_name = self.values[0]
        role = discord.utils.get(guild.roles, name=role_name)

        if role is None:
            await interaction.response.send_message("❌ Rôle introuvable, contacte un admin.", ephemeral=True)
            return

        member = interaction.user
        assignables = ["💼 Équipe", "🤝 Partenaire", "📦 Client", "👀 Nouveau"]
        to_remove = [r for r in member.roles if r.name in assignables]
        await member.remove_roles(*to_remove)
        await member.add_roles(role)
        await interaction.response.send_message(f"✅ Rôle **{role_name}** attribué ! Bienvenue.", ephemeral=True)


class RoleSelectView(discord.ui.View):
    def __init__(self):
        super().__init__(timeout=None)
        self.add_item(RoleSelectMenu())


# ─── UI — PANNEAU DE NAVIGATION ──────────────────────────────────────────────
class NavigationView(discord.ui.View):
    def __init__(self):
        super().__init__(timeout=None)

    @discord.ui.button(label="📚 Ressources", style=discord.ButtonStyle.blurple, custom_id="nav_ressources", row=0)
    async def btn_ressources(self, interaction: discord.Interaction, button: discord.ui.Button):
        guild = interaction.guild
        channels_list = []
        for cat in SERVER_STRUCTURE:
            if cat["name"] == "📁 RESSOURCES CENTRALES":
                for ch in cat["channels"]:
                    c = discord.utils.get(guild.channels, name=ch["name"])
                    if c:
                        channels_list.append(f"→ {c.mention}")
        embed = discord.Embed(
            title="📁 Ressources Centrales",
            description="\n".join(channels_list) or "Aucun salon trouvé.",
            color=0x3498db
        )
        await interaction.response.send_message(embed=embed, ephemeral=True)

    @discord.ui.button(label="📅 Réunions", style=discord.ButtonStyle.blurple, custom_id="nav_reunions", row=0)
    async def btn_reunions(self, interaction: discord.Interaction, button: discord.ui.Button):
        guild = interaction.guild
        ch = discord.utils.get(guild.channels, name="📅-planning-réunions")
        embed = discord.Embed(
            title="📅 Réunions",
            description=(
                f"→ {ch.mention if ch else '#📅-planning-réunions'} pour les ordres du jour\n\n"
                "**Salons vocaux :**\n🎙️ Réunion principale\n🎙️ Brainstorming"
            ),
            color=0x9b59b6
        )
        await interaction.response.send_message(embed=embed, ephemeral=True)

    @discord.ui.button(label="🤖 Assistant IA", style=discord.ButtonStyle.green, custom_id="nav_assistant", row=0)
    async def btn_assistant(self, interaction: discord.Interaction, button: discord.ui.Button):
        guild = interaction.guild
        ch = discord.utils.get(guild.channels, name="🤖-assistant-zona")
        embed = discord.Embed(
            title="🤖 Assistant Zona",
            description=(
                f"L'IA est disponible dans {ch.mention if ch else '#🤖-assistant-zona'}\n\n"
                "**Tu peux lui demander :**\n"
                "• Créer un salon ou un rôle\n"
                "• Lister les salons existants\n"
                "• Envoyer un message quelque part\n"
                "• Répondre à tes questions"
            ),
            color=0x2ecc71
        )
        await interaction.response.send_message(embed=embed, ephemeral=True)

    @discord.ui.button(label="🏢 Projets", style=discord.ButtonStyle.grey, custom_id="nav_projets", row=1)
    async def btn_projets(self, interaction: discord.Interaction, button: discord.ui.Button):
        brands = ["🎬 MP4POD", "⚙️ FLOWAGENT", "🔮 SCHÉMATICA", "👗 STYLEAUGENTE", "🎓 EPA IA", "🎥 BERLIZE"]
        embed = discord.Embed(
            title="🏢 Projets Zona Gensy",
            description=(
                "Chaque projet a sa propre catégorie avec :\n"
                "📰 Fil d'actualités · 📁 Ressources · ✅ Tâches\n\n"
                "**Projets actifs :**\n" + "\n".join(f"• {b}" for b in brands)
            ),
            color=0xe67e22
        )
        await interaction.response.send_message(embed=embed, ephemeral=True)

    @discord.ui.button(label="👥 Équipe", style=discord.ButtonStyle.grey, custom_id="nav_equipe", row=1)
    async def btn_equipe(self, interaction: discord.Interaction, button: discord.ui.Button):
        embed = discord.Embed(
            title="👥 Espace Équipe",
            description=(
                "Réservé aux membres internes.\n\n"
                "🔒 Espace admins\n"
                "✅ Tâches du jour\n"
                "🚀 Onboarding"
            ),
            color=0xe74c3c
        )
        await interaction.response.send_message(embed=embed, ephemeral=True)


# ─── OUTILS IA (FUNCTION CALLING) ────────────────────────────────────────────
AI_TOOLS = [
    {
        "name": "create_channel",
        "description": "Crée un nouveau salon dans une catégorie existante du serveur Discord",
        "input_schema": {
            "type": "object",
            "properties": {
                "channel_name": {"type": "string", "description": "Nom du salon (ex: 📋-mon-salon)"},
                "category_name": {"type": "string", "description": "Nom exact de la catégorie cible"},
                "channel_type": {"type": "string", "enum": ["text", "voice"], "description": "Type de salon"}
            },
            "required": ["channel_name", "category_name"]
        }
    },
    {
        "name": "create_role",
        "description": "Crée un nouveau rôle sur le serveur",
        "input_schema": {
            "type": "object",
            "properties": {
                "role_name": {"type": "string", "description": "Nom du rôle"},
                "color_hex": {"type": "string", "description": "Couleur en hex (ex: #3498db)"}
            },
            "required": ["role_name"]
        }
    },
    {
        "name": "list_channels",
        "description": "Liste tous les salons du serveur par catégorie",
        "input_schema": {"type": "object", "properties": {}}
    },
    {
        "name": "list_roles",
        "description": "Liste tous les rôles du serveur",
        "input_schema": {"type": "object", "properties": {}}
    },
    {
        "name": "send_message_to_channel",
        "description": "Envoie un message texte dans un salon spécifique",
        "input_schema": {
            "type": "object",
            "properties": {
                "channel_name": {"type": "string", "description": "Nom exact du salon"},
                "message": {"type": "string", "description": "Contenu du message"}
            },
            "required": ["channel_name", "message"]
        }
    }
]

async def execute_tool(guild: discord.Guild, tool_name: str, tool_input: dict) -> str:
    """Exécute un outil IA sur le serveur Discord."""

    if tool_name == "create_channel":
        name = tool_input["channel_name"].lower().replace(" ", "-")
        category = discord.utils.get(guild.categories, name=tool_input["category_name"])
        if category is None:
            return f"❌ Catégorie '{tool_input['category_name']}' introuvable."
        if discord.utils.get(guild.channels, name=name):
            return f"⚠️ Le salon '{name}' existe déjà."
        is_voice = tool_input.get("channel_type") == "voice"
        if is_voice:
            await guild.create_voice_channel(name=name, category=category)
        else:
            await guild.create_text_channel(name=name, category=category)
        return f"✅ Salon **{name}** créé dans **{category.name}**."

    elif tool_name == "create_role":
        name = tool_input["role_name"]
        if discord.utils.get(guild.roles, name=name):
            return f"⚠️ Le rôle '{name}' existe déjà."
        color = discord.Color.default()
        if "color_hex" in tool_input:
            try:
                color = discord.Color(int(tool_input["color_hex"].lstrip("#"), 16))
            except Exception:
                pass
        await guild.create_role(name=name, color=color)
        return f"✅ Rôle **{name}** créé."

    elif tool_name == "list_channels":
        lines = []
        for cat in guild.categories:
            lines.append(f"**{cat.name}**")
            for ch in cat.channels:
                icon = "🔊" if isinstance(ch, discord.VoiceChannel) else "💬"
                lines.append(f"  {icon} {ch.name}")
        return "\n".join(lines) or "Aucun salon trouvé."

    elif tool_name == "list_roles":
        roles = [r.name for r in guild.roles if r.name != "@everyone"]
        return "Rôles : " + ", ".join(roles)

    elif tool_name == "send_message_to_channel":
        ch_name = tool_input["channel_name"].lower().replace(" ", "-")
        channel = discord.utils.get(guild.text_channels, name=ch_name)
        if channel is None:
            return f"❌ Salon '{ch_name}' introuvable."
        await channel.send(tool_input["message"])
        return f"✅ Message envoyé dans #{ch_name}."

    return "❌ Outil inconnu."


async def ask_zona_ai(guild: discord.Guild, guild_id: int, user_message: str) -> str:
    """Appelle Claude avec function calling pour gérer le serveur."""

    if guild_id not in ai_histories:
        ai_histories[guild_id] = []

    ai_histories[guild_id].append({"role": "user", "content": user_message})
    if len(ai_histories[guild_id]) > 30:
        ai_histories[guild_id] = ai_histories[guild_id][-30:]

    system_prompt = """Tu es Zona, l'assistant IA du serveur Discord "Zona Gensy".
Zona Gensy est le QG digital d'un écosystème d'entreprises : MP4Pod (vidéo/podcast), Flowagent (automatisation), Schématica (hologrammes), Styleaugente (textile/AR), EPA IA (éducation), Berlize (YouTube).
Tu peux modifier le serveur via les outils disponibles. Sois concis, direct, utile.
Réponds toujours en français. Si on te demande une action, exécute-la via les outils. Sinon, réponds normalement."""

    messages = list(ai_histories[guild_id])

    # Boucle agentique (supporte les appels d'outils chaînés)
    while True:
        response = ai_client.messages.create(
            model="claude-sonnet-4-20250514",
            max_tokens=1024,
            system=system_prompt,
            tools=AI_TOOLS,
            messages=messages
        )

        if response.stop_reason == "end_turn":
            text = next((b.text for b in response.content if hasattr(b, "text")), "")
            ai_histories[guild_id].append({"role": "assistant", "content": response.content})
            return text

        elif response.stop_reason == "tool_use":
            ai_histories[guild_id].append({"role": "assistant", "content": response.content})
            tool_results = []
            for block in response.content:
                if block.type == "tool_use":
                    result = await execute_tool(guild, block.name, block.input)
                    tool_results.append({
                        "type": "tool_result",
                        "tool_use_id": block.id,
                        "content": result
                    })
            messages = list(ai_histories[guild_id])
            messages.append({"role": "user", "content": tool_results})
        else:
            return "❌ Réponse inattendue de l'IA."


# ─── SETUP AUTOMATIQUE DU SERVEUR ────────────────────────────────────────────
async def setup_server(guild: discord.Guild, log_channel: discord.TextChannel):
    await log_channel.send("⚙️ **Démarrage du setup Zona Gensy...**")

    # 1. Supprimer tout sauf le salon de log
    await log_channel.send("🗑️ Nettoyage du serveur existant...")
    for channel in guild.channels:
        if channel.id != log_channel.id:
            try:
                await channel.delete()
                await asyncio.sleep(0.4)
            except Exception:
                pass

    # 2. Créer les rôles
    await log_channel.send("🎭 Création des rôles...")
    created_roles: dict[str, discord.Role] = {}
    for rc in ROLES_CONFIG:
        existing = discord.utils.get(guild.roles, name=rc["name"])
        if existing:
            created_roles[rc["name"]] = existing
        else:
            role = await guild.create_role(name=rc["name"], color=rc["color"], hoist=True)
            created_roles[rc["name"]] = role
            await asyncio.sleep(0.3)

    # 3. Créer catégories et salons
    await log_channel.send("🏗️ Création de la structure...")
    created_channels: dict[str, discord.abc.GuildChannel] = {}

    for cat_cfg in SERVER_STRUCTURE:
        overwrites: dict = {
            guild.default_role: discord.PermissionOverwrite(read_messages=False, send_messages=False)
        }

        if cat_cfg.get("public"):
            overwrites[guild.default_role] = discord.PermissionOverwrite(
                read_messages=True, send_messages=False
            )

        for role_name in cat_cfg.get("allowed_roles", []):
            role = created_roles.get(role_name)
            if role:
                overwrites[role] = discord.PermissionOverwrite(read_messages=True, send_messages=True)

        fondateur = created_roles.get("👑 Fondateur")
        if fondateur:
            overwrites[fondateur] = discord.PermissionOverwrite(administrator=True)

        category = await guild.create_category(cat_cfg["name"], overwrites=overwrites)
        await asyncio.sleep(0.3)

        for ch_cfg in cat_cfg["channels"]:
            if ch_cfg["type"] == "voice":
                ch = await guild.create_voice_channel(ch_cfg["name"], category=category)
            else:
                ch = await guild.create_text_channel(ch_cfg["name"], category=category)
            created_channels[ch_cfg["name"]] = ch
            await asyncio.sleep(0.3)

    # 4. Remplir les salons clés
    await log_channel.send("📝 Remplissage des salons...")

    # 👋 Bienvenue
    bienvenue = created_channels.get("👋-bienvenue")
    if bienvenue:
        embed = discord.Embed(
            title="👋 Bienvenue sur Zona Gensy",
            description=(
                "**Zona Gensy** est le QG digital de l'écosystème.\n\n"
                "Un espace conçu pour :\n"
                "• 📁 Centraliser toutes les ressources\n"
                "• 🤝 Collaborer entre équipes, partenaires et clients\n"
                "• 🤖 Interagir avec l'IA intégrée\n"
                "• 🎯 Piloter chaque projet\n\n"
                "**Commence par choisir ton rôle ci-dessous 👇**"
            ),
            color=0x3498db
        )
        embed.set_footer(text="Zona Gensy — Powered by Claude AI")
        await bienvenue.send(embed=embed, view=RoleSelectView())

    # 🗺️ Navigation
    nav = created_channels.get("🗺️-navigation-du-serveur")
    assistant_ch = created_channels.get("🤖-assistant-zona")
    if nav:
        embed = discord.Embed(
            title="🗺️ Navigation — Zona Gensy",
            description=(
                "Utilise les boutons pour accéder rapidement aux sections.\n\n"
                "**Structure du serveur :**\n"
                "📌 Accueil — règles, annonces, bienvenue\n"
                "🏢 QG — général, idées, réunions, assistant IA\n"
                "📁 Ressources — outils, SOPs, assets, templates\n"
                "🎬 Projets — MP4Pod, Flowagent, Schématica...\n"
                "👥 Équipe — espace interne\n"
                "🤝 Clients — suivi et demandes\n\n"
                f"**Assistant IA** : {assistant_ch.mention if assistant_ch else '#🤖-assistant-zona'} — parle-lui en français 🇫🇷"
            ),
            color=0x9b59b6
        )
        await nav.send(embed=embed, view=NavigationView())

    # 📋 Règles
    regles = created_channels.get("📋-règles-et-charte")
    if regles:
        embed = discord.Embed(
            title="📋 Charte Zona Gensy",
            description=(
                "**Nos 5 piliers :**\n\n"
                "1️⃣ **Transmission** — partager, enseigner, documenter\n"
                "2️⃣ **Excellence artisanale** — craft humain + technologie\n"
                "3️⃣ **Transparence** — vérité, clarté, durée\n"
                "4️⃣ **Innovation utile** — outils qui résolvent de vrais problèmes\n"
                "5️⃣ **Héritage** — construire pour durer\n\n"
                "**Règles :**\n"
                "• Respect mutuel en toutes circonstances\n"
                "• Confidentialité — ce qui est ici reste ici\n"
                "• Feedback constructif, toujours\n"
                "• Bon usage de chaque salon"
            ),
            color=0xe74c3c
        )
        await regles.send(embed=embed)

    # 🤖 Assistant
    if assistant_ch:
        embed = discord.Embed(
            title="🤖 Zona — Assistant IA",
            description=(
                "Je suis **Zona**, ton assistant IA intégré au serveur.\n\n"
                "**Tu peux me demander :**\n"
                "• Créer un salon dans une catégorie\n"
                "• Créer un nouveau rôle\n"
                "• Lister les salons ou rôles existants\n"
                "• Envoyer un message dans un salon\n"
                "• Répondre à n'importe quelle question\n\n"
                "**Exemples :**\n"
                "_\"Crée un salon #réunion-client dans la catégorie CLIENTS\"_\n"
                "_\"Quels sont les salons disponibles ?\"_\n"
                "_\"Crée un rôle Designer en violet\"_\n\n"
                "Parle-moi simplement, en français 🇫🇷"
            ),
            color=0x2ecc71
        )
        await assistant_ch.send(embed=embed)

    await log_channel.send(
        "✅ **Zona Gensy est opérationnel !**\n"
        "→ Attribue-toi le rôle 👑 Fondateur depuis les paramètres Discord.\n"
        "→ Tu peux supprimer ce message de log si tu veux."
    )


# ─── ÉVÉNEMENTS ──────────────────────────────────────────────────────────────
@bot.event
async def on_ready():
    print(f"✅ Bot connecté : {bot.user}")
    bot.add_view(NavigationView())
    bot.add_view(RoleSelectView())
    try:
        synced = await bot.tree.sync()
        print(f"✅ {len(synced)} commande(s) synchronisée(s).")
    except Exception as e:
        print(f"❌ Erreur de sync : {e}")


@bot.event
async def on_member_join(member: discord.Member):
    guild = member.guild
    bienvenue = discord.utils.get(guild.text_channels, name="👋-bienvenue")
    nouveau = discord.utils.get(guild.roles, name="👀 Nouveau")
    if nouveau:
        await member.add_roles(nouveau)
    if bienvenue:
        await bienvenue.send(
            f"👋 Bienvenue **{member.mention}** ! "
            f"Sélectionne ton rôle dans le message épinglé ci-dessus ⬆️"
        )


@bot.event
async def on_message(message: discord.Message):
    if message.author.bot:
        return

    # Canal de l'assistant IA
    if message.channel.name == "🤖-assistant-zona":
        async with message.channel.typing():
            try:
                response = await ask_zona_ai(message.guild, message.guild.id, message.content)
                # Découpe si > 2000 chars (limite Discord)
                if len(response) > 2000:
                    for chunk in [response[i:i+2000] for i in range(0, len(response), 2000)]:
                        await message.channel.send(chunk)
                else:
                    await message.channel.send(response)
            except Exception as e:
                await message.channel.send(f"❌ Erreur IA : {str(e)}")
        return

    await bot.process_commands(message)


# ─── SLASH COMMAND — SETUP ───────────────────────────────────────────────────
@bot.tree.command(name="setup", description="Configure le serveur Zona Gensy (une seule fois)")
@app_commands.checks.has_permissions(administrator=True)
async def setup_command(interaction: discord.Interaction):
    await interaction.response.defer(ephemeral=True)
    channel = interaction.channel
    await interaction.followup.send("🚀 Setup en cours... Ne ferme pas Discord.", ephemeral=True)
    await setup_server(interaction.guild, channel)


# ─── LANCEMENT ───────────────────────────────────────────────────────────────
if __name__ == "__main__":
    if not DISCORD_TOKEN:
        raise ValueError("DISCORD_TOKEN manquant dans les variables d'environnement.")
    if not ANTHROPIC_API_KEY:
        raise ValueError("ANTHROPIC_API_KEY manquant dans les variables d'environnement.")
    bot.run(DISCORD_TOKEN)
