PGDMP  8                    |            hudini    16.4    16.4                0    0    ENCODING    ENCODING        SET client_encoding = 'UTF8';
                      false                       0    0 
   STDSTRINGS 
   STDSTRINGS     (   SET standard_conforming_strings = 'on';
                      false                       0    0 
   SEARCHPATH 
   SEARCHPATH     8   SELECT pg_catalog.set_config('search_path', '', false);
                      false                       1262    16861    hudini    DATABASE     z   CREATE DATABASE hudini WITH TEMPLATE = template0 ENCODING = 'UTF8' LOCALE_PROVIDER = libc LOCALE = 'German_Germany.1252';
    DROP DATABASE hudini;
                postgres    false            �            1259    16867    alembic_version    TABLE     X   CREATE TABLE public.alembic_version (
    version_num character varying(32) NOT NULL
);
 #   DROP TABLE public.alembic_version;
       public         heap    postgres    false            �            1259    18265    api_keys    TABLE       CREATE TABLE public.api_keys (
    id uuid DEFAULT public.uuid_generate_v4() NOT NULL,
    "user" uuid NOT NULL,
    key character varying(64) NOT NULL,
    created timestamp with time zone DEFAULT CURRENT_TIMESTAMP NOT NULL,
    active boolean DEFAULT false NOT NULL
);
    DROP TABLE public.api_keys;
       public         heap    postgres    false            �            1259    18199    gripsbox    TABLE     �  CREATE TABLE public.gripsbox (
    id uuid DEFAULT public.uuid_generate_v4() NOT NULL,
    name character varying NOT NULL,
    size integer NOT NULL,
    type character varying NOT NULL,
    active boolean NOT NULL,
    created timestamp with time zone DEFAULT CURRENT_TIMESTAMP NOT NULL,
    updated timestamp with time zone DEFAULT CURRENT_TIMESTAMP NOT NULL,
    "user" uuid NOT NULL,
    tags json NOT NULL,
    models json
);
    DROP TABLE public.gripsbox;
       public         heap    postgres    false            �            1259    18165    prompts    TABLE       CREATE TABLE public.prompts (
    uuid uuid DEFAULT public.uuid_generate_v4() NOT NULL,
    prompt text NOT NULL,
    status character varying(50) NOT NULL,
    "user" uuid NOT NULL,
    created timestamp with time zone DEFAULT CURRENT_TIMESTAMP NOT NULL
);
    DROP TABLE public.prompts;
       public         heap    postgres    false            �            1259    18179    user_context    TABLE     B  CREATE TABLE public.user_context (
    uuid uuid DEFAULT public.uuid_generate_v4() NOT NULL,
    context_data jsonb NOT NULL,
    "user" uuid NOT NULL,
    thread_id bigint NOT NULL,
    created timestamp with time zone DEFAULT CURRENT_TIMESTAMP NOT NULL,
    updated timestamp with time zone DEFAULT CURRENT_TIMESTAMP
);
     DROP TABLE public.user_context;
       public         heap    postgres    false            �            1259    18153    users    TABLE     �  CREATE TABLE public.users (
    uuid uuid DEFAULT public.uuid_generate_v4() NOT NULL,
    username character varying(50) NOT NULL,
    email character varying(100) NOT NULL,
    created timestamp with time zone DEFAULT CURRENT_TIMESTAMP NOT NULL,
    updated timestamp with time zone DEFAULT CURRENT_TIMESTAMP,
    last_login timestamp with time zone,
    password character varying(128) NOT NULL
);
    DROP TABLE public.users;
       public         heap    postgres    false                      0    16867    alembic_version 
   TABLE DATA                 public          postgres    false    217   �#                 0    18265    api_keys 
   TABLE DATA                 public          postgres    false    222   J$                 0    18199    gripsbox 
   TABLE DATA                 public          postgres    false    221   �%                 0    18165    prompts 
   TABLE DATA                 public          postgres    false    219   �%                 0    18179    user_context 
   TABLE DATA                 public          postgres    false    220   &                 0    18153    users 
   TABLE DATA                 public          postgres    false    218   &       h           2606    16871 #   alembic_version alembic_version_pkc 
   CONSTRAINT     j   ALTER TABLE ONLY public.alembic_version
    ADD CONSTRAINT alembic_version_pkc PRIMARY KEY (version_num);
 M   ALTER TABLE ONLY public.alembic_version DROP CONSTRAINT alembic_version_pkc;
       public            postgres    false    217            v           2606    18271    api_keys api_keys_pkey 
   CONSTRAINT     T   ALTER TABLE ONLY public.api_keys
    ADD CONSTRAINT api_keys_pkey PRIMARY KEY (id);
 @   ALTER TABLE ONLY public.api_keys DROP CONSTRAINT api_keys_pkey;
       public            postgres    false    222            t           2606    18208    gripsbox gripsbox_pkey 
   CONSTRAINT     T   ALTER TABLE ONLY public.gripsbox
    ADD CONSTRAINT gripsbox_pkey PRIMARY KEY (id);
 @   ALTER TABLE ONLY public.gripsbox DROP CONSTRAINT gripsbox_pkey;
       public            postgres    false    221            p           2606    18173    prompts prompts_pkey 
   CONSTRAINT     T   ALTER TABLE ONLY public.prompts
    ADD CONSTRAINT prompts_pkey PRIMARY KEY (uuid);
 >   ALTER TABLE ONLY public.prompts DROP CONSTRAINT prompts_pkey;
       public            postgres    false    219            r           2606    18188    user_context user_context_pkey 
   CONSTRAINT     ^   ALTER TABLE ONLY public.user_context
    ADD CONSTRAINT user_context_pkey PRIMARY KEY (uuid);
 H   ALTER TABLE ONLY public.user_context DROP CONSTRAINT user_context_pkey;
       public            postgres    false    220            j           2606    18164    users users_email_key 
   CONSTRAINT     Q   ALTER TABLE ONLY public.users
    ADD CONSTRAINT users_email_key UNIQUE (email);
 ?   ALTER TABLE ONLY public.users DROP CONSTRAINT users_email_key;
       public            postgres    false    218            l           2606    18160    users users_pkey 
   CONSTRAINT     P   ALTER TABLE ONLY public.users
    ADD CONSTRAINT users_pkey PRIMARY KEY (uuid);
 :   ALTER TABLE ONLY public.users DROP CONSTRAINT users_pkey;
       public            postgres    false    218            n           2606    18162    users users_username_key 
   CONSTRAINT     W   ALTER TABLE ONLY public.users
    ADD CONSTRAINT users_username_key UNIQUE (username);
 B   ALTER TABLE ONLY public.users DROP CONSTRAINT users_username_key;
       public            postgres    false    218            {           2620    18278    users trigger_create_api_key    TRIGGER     �   CREATE TRIGGER trigger_create_api_key AFTER INSERT ON public.users FOR EACH ROW EXECUTE FUNCTION public.create_api_key_for_user();
 5   DROP TRIGGER trigger_create_api_key ON public.users;
       public          postgres    false    218            |           2620    18210     gripsbox update_gripsbox_modtime    TRIGGER     �   CREATE TRIGGER update_gripsbox_modtime BEFORE UPDATE ON public.gripsbox FOR EACH ROW EXECUTE FUNCTION public.update_modified_column();
 9   DROP TRIGGER update_gripsbox_modtime ON public.gripsbox;
       public          postgres    false    221            z           2606    18272    api_keys api_keys_user_fkey    FK CONSTRAINT     �   ALTER TABLE ONLY public.api_keys
    ADD CONSTRAINT api_keys_user_fkey FOREIGN KEY ("user") REFERENCES public.users(uuid) ON DELETE CASCADE;
 E   ALTER TABLE ONLY public.api_keys DROP CONSTRAINT api_keys_user_fkey;
       public          postgres    false    222    4716    218            y           2606    18288    gripsbox fk_user    FK CONSTRAINT     �   ALTER TABLE ONLY public.gripsbox
    ADD CONSTRAINT fk_user FOREIGN KEY ("user") REFERENCES public.users(uuid) ON DELETE CASCADE;
 :   ALTER TABLE ONLY public.gripsbox DROP CONSTRAINT fk_user;
       public          postgres    false    218    4716    221            w           2606    18174    prompts prompts_user_fkey    FK CONSTRAINT     �   ALTER TABLE ONLY public.prompts
    ADD CONSTRAINT prompts_user_fkey FOREIGN KEY ("user") REFERENCES public.users(uuid) ON DELETE CASCADE;
 C   ALTER TABLE ONLY public.prompts DROP CONSTRAINT prompts_user_fkey;
       public          postgres    false    218    219    4716            x           2606    18189 #   user_context user_context_user_fkey    FK CONSTRAINT     �   ALTER TABLE ONLY public.user_context
    ADD CONSTRAINT user_context_user_fkey FOREIGN KEY ("user") REFERENCES public.users(uuid) ON DELETE CASCADE;
 M   ALTER TABLE ONLY public.user_context DROP CONSTRAINT user_context_user_fkey;
       public          postgres    false    220    218    4716               e   x���v
Q���W((M��L�K�I�M�L�/K-*���SЀ2��Js5�}B]�4�-�L,��L-����5������|<�C\���C<<�ܭ��� <�         v  x���Oo�@��|�U.�*�v����B���1�K��]W6$�lH�~���\z�uf�4�7Q���R�i��[~)����s�Ӣ�ҏ�ݭ��u��&�k�T��[�������YN	� XKQ`n]��SsF� ��f8BC��)�Lv��[�(V�� )��MUCj�`g؈�Ue�=пG���[��/;pK���'u]�s,_�X���� �11�
tzl�%5J%��ͭ��h�ċM4K�C��$]F�o��?a)�2��F�w��ز"��1��BIݷ��9�7 s���<&L'kh��)Ӫ ����}\�4���.�$՚��Cq���x���~Xf�|���.��ө�~&����tK�3| 6�&         
   x���             
   x���             
   x���             �  x����n�@��~�YXr�2��秛�nC	�1�tU0�'���IZ?}�R�Q�f��9�~����huy� ?Jb������tہ��7��R�����+��@�ju�æ)_�Nu��zc*4���<�4L/W�lⲂђ(�,!��g�6qiI%��=����k}ؚ��|�����S�)�؅D B=�<� ,� �L_�"=*<�?]a�6��0�����b}������m��u���v,����Y�tw��mz���e����,P���8�8���|�A'?��4���e�+�cA >ن�k�bVB̄.�K�r���/Me����T/���`�a�dI)~��_@���_��a�������h��ױ]Q�<��r��C�뾎���4�f��� U�w,�F���     