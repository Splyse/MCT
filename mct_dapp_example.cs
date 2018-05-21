using Neo.SmartContract.Framework;
using Neo.SmartContract.Framework.Services.Neo;
using Neo.SmartContract.Framework.Services.System;
using System;
using System.ComponentModel;
using System.Numerics;

namespace Neo.SmartContract
{
	public class Mct_Dapp_Example : Framework.SmartContract
	{
		public delegate object NEP5Contract(string method, object[] args);
		
		//MainNet
		//[AppCall("a87cc2a513f5d8b4a42432343687c2127c60bc3f".ToScriptHash())]
		//public static extern int MCTContract (string operation, object[] args);

		//TestNet
		[AppCall("c186bcb4dc6db8e08be09191c6173456144c4b8d".ToScriptHash())] // ScriptHash
		public static extern int MCTContract (string operation, object[] args);

		public static void Main (string operation, params object[] args)
		{
			switch (operation)
			{
				case "Put":
					return put_mct((object)args);
				case "Get":
					return get_mct((object)args);
				case "Delete":
					return delete_mct((object)args);
				default:
					return false;
			}
		}

		private static bool put_mct(object[] data)
		{
			if (!Runtime.CheckWitness(owner)) return false;
			byte[] value = get_mct((object)data[0]);
			if (value != null) return false;
      
			return MCTContract("Put", data);
		}

		private static byte[] get_mct(object[] key)
		{
			return MCTContract("Get", key);
		}

		private static bool delete_mct(object[] key)
		{
			byte[] owner = get_mct(key);
			if (owner == null) return false;
			if (!Runtime.CheckWitness(owner)) return false;
      
			return MCTContract("Delete", key);
		}
	}
}
